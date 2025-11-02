"""
AI-powered metadata generator using OpenAI API.
Generates rich SEO metadata for URLs based on their path and context.
"""
import os
import logging
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)


def generate_metadata_with_ai(url_path: str, page_name: Optional[str] = None) -> Dict[str, str]:
    """
    Generate SEO metadata for a URL using OpenAI.
    
    Args:
        url_path: The URL path (e.g., '/about/', '/services/interior-design/')
        page_name: Optional human-readable page name for context
    
    Returns:
        Dict with 'meta_title', 'meta_description', 'meta_keywords'
    
    Raises:
        ValueError: If OpenAI API key is not configured
    """
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("OpenAI library not installed. Run: pip install openai")
        raise ValueError("OpenAI library not installed")
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY not configured")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Build context from URL path
    url_context = infer_context_from_url(url_path, page_name)
    
    # Generate metadata with AI
    try:
        prompt = build_prompt(url_path, url_context, page_name)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective
            messages=[
                {"role": "system", "content": "You are an expert SEO specialist creating metadata for a luxury construction, landscaping, and interior design company in Dubai called Hammer Group."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        ai_output = response.choices[0].message.content
        metadata = parse_ai_output(ai_output)
        
        logger.info(f"Generated metadata for {url_path}")
        return metadata
        
    except Exception as e:
        logger.error(f"Error generating metadata with AI: {str(e)}")
        # Fallback to basic metadata
        return generate_fallback_metadata(url_path, page_name)


def infer_context_from_url(url_path: str, page_name: Optional[str] = None) -> Dict[str, str]:
    """
    Infer page context from URL path to help AI generate better metadata.
    """
    context = {
        'industry': 'Luxury construction, landscaping, and interior design',
        'location': 'Dubai, UAE',
        'company': 'Hammer Group',
        'years_experience': '20+ years',
        'style': 'Premium, luxury, high-end'
    }
    
    # Parse URL to determine page type
    url_lower = url_path.lower()
    
    if url_lower == '/' or 'home' in url_lower:
        context['page_type'] = 'homepage'
        context['focus'] = 'luxury villa construction, landscaping, and interior design services'
    elif 'about' in url_lower:
        context['page_type'] = 'about'
        context['focus'] = 'company history, team expertise, and professional experience'
    elif 'contact' in url_lower:
        context['page_type'] = 'contact'
        context['focus'] = 'getting in touch, consultation, and inquiries'
    elif 'landscape' in url_lower or 'landscaping' in url_lower:
        context['page_type'] = 'service'
        context['focus'] = 'landscape design, outdoor spaces, pool design, garden design'
    elif 'interior' in url_lower:
        context['page_type'] = 'service'
        context['focus'] = 'interior design, luxury home interiors, residential fit-out'
    elif 'facility' in url_lower or 'maintenance' in url_lower:
        context['page_type'] = 'service'
        context['focus'] = 'facility management, property maintenance, aftercare services'
    elif 'service' in url_lower:
        context['page_type'] = 'services_index'
        context['focus'] = 'comprehensive construction, design, and management services'
    elif 'project' in url_lower or 'portfolio' in url_lower:
        context['page_type'] = 'portfolio'
        context['focus'] = 'completed projects, case studies, luxury homes and spaces'
    elif 'insight' in url_lower or 'blog' in url_lower:
        context['page_type'] = 'blog'
        context['focus'] = 'design insights, construction tips, industry trends'
    else:
        context['page_type'] = 'generic'
        context['focus'] = 'luxury construction and design services in Dubai'
    
    return context


def build_prompt(url_path: str, context: Dict[str, str], page_name: Optional[str] = None) -> str:
    """
    Build the prompt for OpenAI to generate metadata.
    """
    prompt = f"""Generate SEO metadata for a webpage with these details:

URL Path: {url_path}
Page Name: {page_name or 'Not specified'}
Page Type: {context['page_type']}
Focus: {context['focus']}

Company Context:
- Name: {context['company']}
- Industry: {context['industry']}
- Location: {context['location']}
- Experience: {context['years_experience']}
- Style: {context['style']}

Requirements:
1. Meta Title: 50-70 characters, compelling and keyword-rich
2. Meta Description: 150-160 characters, persuasive and action-oriented
3. Meta Keywords: 5-10 relevant keywords, comma-separated

Format your response exactly as:
TITLE: [your title here]
DESCRIPTION: [your description here]
KEYWORDS: [keyword1, keyword2, keyword3, etc.]

Make it specific to this page, highly relevant for Dubai audience, and emphasize luxury and premium quality."""
    
    return prompt


def parse_ai_output(ai_output: str) -> Dict[str, str]:
    """
    Parse the AI output to extract structured metadata.
    """
    metadata = {
        'meta_title': '',
        'meta_description': '',
        'meta_keywords': ''
    }
    
    try:
        # Extract title
        title_match = re.search(r'TITLE:\s*(.+?)(?=\n|DESCRIPTION:)', ai_output, re.IGNORECASE | re.DOTALL)
        if title_match:
            metadata['meta_title'] = title_match.group(1).strip()
        
        # Extract description
        desc_match = re.search(r'DESCRIPTION:\s*(.+?)(?=\n|KEYWORDS:)', ai_output, re.IGNORECASE | re.DOTALL)
        if desc_match:
            metadata['meta_description'] = desc_match.group(1).strip()
        
        # Extract keywords
        keywords_match = re.search(r'KEYWORDS:\s*(.+?)(?=\n|$)', ai_output, re.IGNORECASE | re.DOTALL)
        if keywords_match:
            metadata['meta_keywords'] = keywords_match.group(1).strip()
            
        # Ensure lengths are within limits
        if len(metadata['meta_title']) > 140:
            metadata['meta_title'] = metadata['meta_title'][:137] + '...'
        if len(metadata['meta_description']) > 200:
            metadata['meta_description'] = metadata['meta_description'][:197] + '...'
        if len(metadata['meta_keywords']) > 255:
            metadata['meta_keywords'] = metadata['meta_keywords'][:252] + '...'
            
    except Exception as e:
        logger.error(f"Error parsing AI output: {str(e)}")
        raise
    
    return metadata


def generate_fallback_metadata(url_path: str, page_name: Optional[str] = None) -> Dict[str, str]:
    """
    Generate basic metadata without AI as a fallback.
    """
    url_lower = url_path.lower()
    
    if url_lower == '/' or 'home' in url_lower:
        return {
            'meta_title': 'Luxury Villa Construction, Landscaping & Interior Design in Dubai | Hammer Group',
            'meta_description': 'Premier construction, landscaping, and interior design services in Dubai. 20+ years transforming visions into exceptional living spaces.',
            'meta_keywords': 'Dubai construction, villa construction, landscaping Dubai, interior design Dubai, luxury homes'
        }
    elif 'about' in url_lower:
        return {
            'meta_title': 'About Hammer Group | Dubai Luxury Construction Experts',
            'meta_description': '20+ years delivering exceptional construction, landscaping, and interior design in Dubai. Meet our team of specialists.',
            'meta_keywords': 'about us, Dubai construction company, luxury builders, team Dubai'
        }
    elif 'contact' in url_lower:
        return {
            'meta_title': 'Contact Us | Hammer Group Dubai',
            'meta_description': 'Get in touch with Hammer Group for luxury construction, landscaping, and interior design services in Dubai.',
            'meta_keywords': 'contact, Dubai construction contact, get quote, consultation Dubai'
        }
    elif 'landscape' in url_lower or 'landscaping' in url_lower:
        return {
            'meta_title': 'Landscape Design & Build Dubai | Hammer Group',
            'meta_description': 'Premium landscape design & build in Dubai. Native planting, custom pools, pergolas, and architectural lighting.',
            'meta_keywords': 'landscape design Dubai, pool design, outdoor landscaping, garden design UAE'
        }
    elif 'interior' in url_lower:
        return {
            'meta_title': 'Interior Design & Build Dubai | Hammer Group',
            'meta_description': 'Transform your space with premium interior design & build services in Dubai.',
            'meta_keywords': 'interior design Dubai, home interiors, luxury design, residential fit-out'
        }
    elif 'facility' in url_lower or 'maintenance' in url_lower:
        return {
            'meta_title': 'Facility Management Dubai | Hammer Group',
            'meta_description': 'Professional facility management and maintenance services in Dubai.',
            'meta_keywords': 'facility management Dubai, property maintenance, building maintenance'
        }
    elif 'service' in url_lower:
        return {
            'meta_title': 'Our Services | Luxury Construction & Design Dubai',
            'meta_description': 'Comprehensive construction, landscaping, and interior design services in Dubai.',
            'meta_keywords': 'Dubai construction services, landscaping services, interior design services'
        }
    elif 'project' in url_lower:
        return {
            'meta_title': 'Our Projects | Luxury Construction Portfolio Dubai',
            'meta_description': 'Browse our portfolio of luxury construction, landscaping, and design projects in Dubai.',
            'meta_keywords': 'Dubai projects, construction portfolio, case studies, luxury homes'
        }
    elif 'insight' in url_lower or 'blog' in url_lower:
        return {
            'meta_title': 'Insights | Dubai Construction & Design Blog',
            'meta_description': 'Stay updated with the latest insights on construction, landscaping, and interior design trends in Dubai.',
            'meta_keywords': 'Dubai blog, construction insights, design trends, industry news UAE'
        }
    else:
        # Generic fallback
        safe_name = page_name or url_path.strip('/').replace('-', ' ').replace('/', ' ').title()
        return {
            'meta_title': f'{safe_name} | Hammer Group Dubai',
            'meta_description': f'Explore {safe_name.lower()} at Hammer Group, Dubai\'s premier construction and design specialists.',
            'meta_keywords': f'Dubai, construction, design, luxury, Hammer Group'
        }

