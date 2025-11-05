# Spam Blocking System - Setup Guide

## Overview

A comprehensive spam blocking system has been implemented for your contact form. It includes:

1. **Rate Limiting** - Prevents multiple submissions from the same email/IP
2. **Email & IP Blacklisting** - Block specific emails and IP addresses
3. **Content Filtering** - Detects spam keywords and suspicious patterns
4. **Honeypot Fields** - Hidden fields that trap bots
5. **Submission Tracking** - Logs all submissions for analysis

## Features Implemented

### 1. Models Added
- `BlockedEmail` - Store blocked email addresses
- `BlockedIP` - Store blocked IP addresses  
- `FormSubmission` - Track all form submissions for rate limiting

### 2. Spam Detection (`myApp/spam_detection.py`)
- Rate limiting (per email/IP per hour/day)
- Email pattern detection
- Spam keyword filtering
- Content analysis (links, capitalization, length)
- Automatic blocking for high spam scores (optional)

### 3. Enhanced Contact Form (`myApp/forms.py`)
- Dual honeypot fields (honeypot + website)
- Enhanced validation (name length, message length, email format)
- Better error messages

### 4. Updated Contact View (`myApp/views.py`)
- Spam validation before processing
- Automatic blocking for high spam scores (optional)
- Submission logging for rate limiting

### 5. Admin Interface (`myApp/admin.py`)
- Manage blocked emails
- Manage blocked IPs
- View form submission history

## Setup Instructions

### Step 1: Run Database Migration

```bash
cd myProject
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Configure Settings (Optional)

Add these to your `settings.py` to customize spam detection:

```python
# Spam blocking configuration
SPAM_RATE_LIMITS = {
    'email_per_hour': 3,  # Max submissions per email per hour
    'ip_per_hour': 5,     # Max submissions per IP per hour
    'ip_per_day': 10,     # Max submissions per IP per day
}

SPAM_THRESHOLD = 50  # Spam score threshold (0-100)

# Auto-block emails/IPs with very high spam scores (default: False)
AUTO_BLOCK_SPAM = False  # Set to True to enable automatic blocking

# Enable debug messages in spam rejection (default: False)
SPAM_DEBUG = False  # Set to True to see spam scores in error messages
```

### Step 3: Block Known Spam Emails/IPs

You can manually block emails or IPs through the Django admin:

1. Go to Django admin: `/admin/`
2. Navigate to **Blocked Emails** or **Blocked IPs**
3. Add the email address or IP you want to block
4. Optionally add a reason for tracking

## How to Use

### Blocking Spam Emails

1. **Via Admin Interface:**
   - Go to `/admin/myApp/blockedemail/`
   - Click "Add Blocked Email"
   - Enter the email address and reason
   - Save

2. **Automatically (if enabled):**
   - Set `AUTO_BLOCK_SPAM = True` in settings
   - Emails with spam score ≥ 70 will be automatically blocked

### Blocking IP Addresses

1. **Via Admin Interface:**
   - Go to `/admin/myApp/blockedip/`
   - Click "Add Blocked IP"
   - Enter the IP address and reason
   - Save

2. **Automatically (if enabled):**
   - Set `AUTO_BLOCK_SPAM = True` in settings
   - IPs with spam score ≥ 70 will be automatically blocked

### Viewing Form Submissions

1. Go to `/admin/myApp/formsubmission/`
2. View all form submissions with:
   - Email address
   - Name
   - IP address
   - Service type
   - Submission timestamp
   - Message preview

## Spam Detection Rules

The system checks for:

1. **Blocked Email/IP** - Immediate rejection
2. **Rate Limiting** - Too many submissions in short time
3. **Suspicious Email Patterns** - Random alphanumeric emails, suspicious TLDs
4. **Spam Keywords** - Common spam terms (viagra, casino, etc.)
5. **Excessive Links** - More than 2 links in message
6. **Excessive Capitalization** - More than 50% caps
7. **Message Too Short** - Less than 10 characters
8. **Suspicious Phone Format** - Invalid phone patterns

## Customizing Spam Keywords

Edit `myApp/spam_detection.py` and modify the `SPAM_KEYWORDS` list:

```python
SPAM_KEYWORDS = [
    'viagra', 'cialis', 'casino', 'poker', 'loan', 'credit', 'debt',
    # Add your own keywords here
]
```

## Testing

To test the spam blocking:

1. **Test Rate Limiting:**
   - Submit the form 3+ times from the same email within an hour
   - Should get rate limit error

2. **Test Blocked Email:**
   - Add your email to Blocked Emails in admin
   - Try to submit form with that email
   - Should get blocked email error

3. **Test Honeypot:**
   - Inspect the form HTML
   - Find the hidden `honeypot` or `website` field
   - Fill it in and submit
   - Should get "Spam detected" error

4. **Test Spam Keywords:**
   - Submit form with message containing "viagra" or other spam keywords
   - Should get spam rejection

## Monitoring

Check the Django admin regularly to:
- Review new form submissions
- Identify patterns in spam attempts
- Manually block persistent spammers
- Monitor rate limiting effectiveness

## Troubleshooting

### Legitimate submissions are being blocked

1. **Lower the spam threshold:**
   ```python
   SPAM_THRESHOLD = 30  # Lower = less strict
   ```

2. **Disable auto-blocking:**
   ```python
   AUTO_BLOCK_SPAM = False
   ```

3. **Review blocked emails/IPs:**
   - Check if legitimate emails/IPs are in the blocklist
   - Remove them from admin if needed

### Rate limiting too strict

Adjust in settings:
```python
SPAM_RATE_LIMITS = {
    'email_per_hour': 5,  # Increase from 3
    'ip_per_hour': 10,    # Increase from 5
    'ip_per_day': 20,     # Increase from 10
}
```

### Need to see spam scores for debugging

Enable debug mode:
```python
SPAM_DEBUG = True
```

This will show spam scores and reasons in error messages (useful for testing).

## Files Modified/Created

1. **New Files:**
   - `myApp/spam_detection.py` - Spam detection utilities

2. **Modified Files:**
   - `myApp/models.py` - Added BlockedEmail, BlockedIP, FormSubmission models
   - `myApp/forms.py` - Enhanced ContactForm with validation
   - `myApp/views.py` - Added spam checking to contact view
   - `myApp/admin.py` - Added admin interfaces for spam management
   - `myApp/templates/partials/contact.html` - Added honeypot fields and improved error handling

## Next Steps

After running migrations:

1. Test the spam blocking system
2. Monitor form submissions in admin
3. Adjust rate limits and thresholds as needed
4. Block known spam emails/IPs as they appear
5. Consider adding CAPTCHA for additional protection (optional)

## Optional: Adding CAPTCHA

For even stronger protection, you can add Google reCAPTCHA or hCaptcha:

1. Install a Django CAPTCHA package (e.g., `django-recaptcha`)
2. Add CAPTCHA field to `ContactForm`
3. Validate CAPTCHA in the contact view

This is optional since the current system provides strong protection already.

