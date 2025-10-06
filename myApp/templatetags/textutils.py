# myApp/templatetags/textutils.py
from django import template
import re

register = template.Library()

@register.filter
def trim(value: str):
    return (value or "").strip()

@register.filter
def squish(value: str):
    """Collapse runs of whitespace/newlines to a single space."""
    return re.sub(r"\s+", " ", (value or "")).strip()
