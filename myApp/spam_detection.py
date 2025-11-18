# myApp/spam_detection.py
"""
Spam detection utilities for contact form submissions.
Includes rate limiting, blacklist checking, and content filtering.
"""
import re
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from .models import BlockedEmail, BlockedIP, FormSubmission

logger = logging.getLogger(__name__)


# Common spam keywords/phrases (add more as needed)
SPAM_KEYWORDS = [
    'viagra', 'cialis', 'casino', 'poker', 'loan', 'credit', 'debt',
    'seo', 'backlink', 'buy followers', 'get rich', 'work from home',
    'make money', 'click here', 'limited time', 'act now', 'urgent',
    'congratulations', 'winner', 'prize', 'free money', 'guaranteed',
    'no credit check', 'risk free', 'mlm', 'pyramid', 'bitcoin',
    'cryptocurrency', 'forex', 'trading robot', 'weight loss',
    'diet pill', 'penis enlargement', 'hair loss', 'anti aging',
]

# Suspicious email patterns
SUSPICIOUS_EMAIL_PATTERNS = [
    r'^[a-z0-9]{8,}@(hotmail|gmail|yahoo|outlook)\.(com|net|org)$',  # Random alphanumeric
    r'^\d+@',  # Starts with numbers
    r'@.*\.(tk|ml|ga|cf|gq)$',  # Suspicious TLDs
]

# Rate limiting settings (can be overridden in settings.py)
DEFAULT_RATE_LIMITS = {
    'email_per_hour': 3,  # Max 3 submissions per hour per email
    'ip_per_hour': 5,     # Max 5 submissions per hour per IP
    'ip_per_day': 10,     # Max 10 submissions per day per IP
}


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_email_blocked(email):
    """Check if email is in the blocklist"""
    return BlockedEmail.objects.filter(
        email__iexact=email,
        is_active=True
    ).exists()


def is_ip_blocked(ip_address):
    """Check if IP is in the blocklist"""
    if not ip_address:
        return False
    return BlockedIP.objects.filter(
        ip_address=ip_address,
        is_active=True
    ).exists()


def is_suspicious_email(email):
    """Check if email matches suspicious patterns"""
    email_lower = email.lower()
    for pattern in SUSPICIOUS_EMAIL_PATTERNS:
        if re.match(pattern, email_lower):
            return True
    return False


def contains_spam_keywords(text):
    """Check if text contains spam keywords"""
    if not text:
        return False
    text_lower = text.lower()
    for keyword in SPAM_KEYWORDS:
        if keyword in text_lower:
            return True
    return False


def check_rate_limit_email(email, time_window_minutes=60):
    """Check if email has exceeded rate limit"""
    limits = getattr(settings, 'SPAM_RATE_LIMITS', DEFAULT_RATE_LIMITS)
    max_per_hour = limits.get('email_per_hour', 3)
    
    cutoff_time = timezone.now() - timedelta(minutes=time_window_minutes)
    recent_submissions = FormSubmission.objects.filter(
        email__iexact=email,
        submitted_at__gte=cutoff_time
    ).count()
    
    return recent_submissions >= max_per_hour


def check_rate_limit_ip(ip_address, time_window_minutes=60):
    """Check if IP has exceeded rate limit"""
    if not ip_address:
        return False
    
    limits = getattr(settings, 'SPAM_RATE_LIMITS', DEFAULT_RATE_LIMITS)
    max_per_hour = limits.get('ip_per_hour', 5)
    
    cutoff_time = timezone.now() - timedelta(minutes=time_window_minutes)
    recent_submissions = FormSubmission.objects.filter(
        ip_address=ip_address,
        submitted_at__gte=cutoff_time
    ).count()
    
    return recent_submissions >= max_per_hour


def check_daily_rate_limit_ip(ip_address):
    """Check if IP has exceeded daily rate limit"""
    if not ip_address:
        return False
    
    limits = getattr(settings, 'SPAM_RATE_LIMITS', DEFAULT_RATE_LIMITS)
    max_per_day = limits.get('ip_per_day', 10)
    
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_submissions = FormSubmission.objects.filter(
        ip_address=ip_address,
        submitted_at__gte=today_start
    ).count()
    
    return today_submissions >= max_per_day


def check_spam_score(email, name, message, phone=None):
    """
    Calculate spam score based on various factors.
    Returns (is_spam: bool, score: int, reasons: list)
    """
    score = 0
    reasons = []
    
    # Check blocked email
    if is_email_blocked(email):
        return True, 100, ['Email is blocked']
    
    # Check suspicious email pattern
    if is_suspicious_email(email):
        score += 30
        reasons.append('Suspicious email pattern')
    
    # Check spam keywords in message
    if contains_spam_keywords(message):
        score += 40
        reasons.append('Contains spam keywords')
    
    # Check spam keywords in name
    if contains_spam_keywords(name):
        score += 20
        reasons.append('Name contains spam keywords')
    
    # Check for excessive links in message
    link_count = len(re.findall(r'http[s]?://', message, re.IGNORECASE))
    if link_count > 2:
        score += 25
        reasons.append(f'Too many links ({link_count})')
    
    # Check for excessive capitalization
    if len(message) > 20:
        caps_ratio = sum(1 for c in message if c.isupper()) / len(message)
        if caps_ratio > 0.5:
            score += 15
            reasons.append('Excessive capitalization')
    
    # Check message length (too short might be spam)
    if len(message.strip()) < 10:
        score += 10
        reasons.append('Message too short')
    
    # Check for suspicious phone patterns
    if phone:
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', phone)
        # Check if phone is too short or too long
        if len(digits_only) < 7 or len(digits_only) > 15:
            score += 5
            reasons.append('Suspicious phone number format')
    
    # Threshold for spam detection
    spam_threshold = getattr(settings, 'SPAM_THRESHOLD', 50)
    is_spam = score >= spam_threshold
    
    return is_spam, score, reasons


def record_submission(email, ip_address, name, service, message):
    """Record a form submission for rate limiting tracking"""
    FormSubmission.objects.create(
        email=email,
        ip_address=ip_address,
        name=name,
        service=service or 'General',
        message_preview=message[:200] if message else '',
    )


def validate_contact_submission(request, form_data):
    """
    Main validation function for contact form submissions.
    Returns (is_valid: bool, error_message: str, should_block: bool)
    """
    email = form_data.get('email', '').strip().lower()
    name = form_data.get('name', '').strip()
    message = form_data.get('message', '').strip()
    phone = form_data.get('phone', '').strip()
    
    if not email or not name or not message:
        return False, "Missing required fields", False
    
    ip_address = get_client_ip(request)
    
    # SKIP SPAM DETECTION ON LOCALHOST (for testing)
    localhost_ips = ['127.0.0.1', '::1', 'localhost']
    is_localhost = (
        ip_address in localhost_ips or 
        (ip_address and ip_address.startswith('127.')) or 
        (ip_address and ip_address.startswith('::1')) or
        getattr(settings, 'DEBUG', False)  # Also skip if DEBUG mode
    )
    
    if is_localhost:
        logger.info(f"🧪 Skipping spam detection for localhost/testing: {ip_address}")
        return True, None, False
    
    # Check blocklists
    if is_email_blocked(email):
        return False, "Your email address has been blocked. Please contact us directly.", True
    
    if is_ip_blocked(ip_address):
        return False, "Your IP address has been blocked. Please contact us directly.", True
    
    # Check rate limits
    if check_rate_limit_email(email):
        return False, "Too many submissions from this email address. Please wait before submitting again.", False
    
    if check_rate_limit_ip(ip_address):
        return False, "Too many submissions from your location. Please wait before submitting again.", False
    
    if check_daily_rate_limit_ip(ip_address):
        return False, "Daily submission limit reached. Please try again tomorrow.", False
    
    # Check spam score
    is_spam, score, reasons = check_spam_score(email, name, message, phone)
    if is_spam:
        error_msg = "Your submission appears to be spam and was rejected."
        if getattr(settings, 'SPAM_DEBUG', False):
            error_msg += f" (Score: {score}, Reasons: {', '.join(reasons)})"
        return False, error_msg, score >= 70  # Block if score is very high
    
    return True, None, False

