from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.conf import settings
import json
import re

try:
    import bleach  # type: ignore
except Exception:  # pragma: no cover
    bleach = None

register = template.Library()


def _linkify_text(text):
    """Convert plain URLs in text to clickable HTML links"""
    if not text:
        return text
    
    # Skip if text already contains HTML anchor tags (to avoid double-processing)
    if '<a ' in text.lower() or '</a>' in text.lower():
        return text
    
    # URL pattern - matches http:// and https:// URLs (more comprehensive)
    # Matches URLs that start with http:// or https:// and continue until whitespace or common punctuation
    url_pattern = r'(https?://[^\s<>&"\'`\[\](){}|\\^]+[^\s<>&"\'`\[\](){}|\\^.,;:!?])'
    
    def make_link(match):
        url = match.group(1)
        # Escape the URL for display in text (href doesn't need escaping, just quotes)
        # Replace any quotes in URL to prevent breaking HTML attribute
        safe_url = url.replace('"', '&quot;').replace("'", '&#x27;')
        escaped_display = escape(url)  # Escape HTML for text content
        return f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer" class="text-[#18AFAB] underline decoration-[#18AFAB]/30 hover:decoration-[#18AFAB] hover:text-[#159d99] font-medium transition-all">{escaped_display}</a>'
    
    # Only linkify if text doesn't already contain HTML tags (to avoid double-processing)
    if '<' in text and '>' in text:
        # Text already contains HTML, don't linkify (might already have links)
        return text
    
    return re.sub(url_pattern, make_link, text)


def _render_block(b):
    t = b.get("type")
    d = b.get("data", {})
    if t == "paragraph":
        text = d.get("text", "")
        linked_text = _linkify_text(text)
        return f'<p class="mb-4">{linked_text}</p>'
    if t == "header":
        level = d.get("level", 2)
        text = d.get("text", "")
        linked_text = _linkify_text(text)
        if level == 3:
            return f'<h3 class="text-xl font-semibold mt-6 mb-3">{linked_text}</h3>'
        return f'<h2 class="text-2xl font-bold mt-8 mb-4">{linked_text}</h2>'
    if t == "list":
        style = d.get("style", "unordered")
        items = "".join([f"<li>{_linkify_text(i)}</li>" for i in d.get("items", [])])
        cls = "list-disc pl-6 mb-4" if style == "unordered" else "list-decimal pl-6 mb-4"
        tag = "ul" if style == "unordered" else "ol"
        return f"<{tag} class='{cls}'>{items}</{tag}>"
    if t == "quote":
        return (
            f"<blockquote class='border-l-4 pl-4 italic my-6'>{d.get('text','')}"
            f"<div class='text-sm mt-2 opacity-70'>{d.get('caption','')}</div></blockquote>"
        )
    if t == "code":
        return f"<pre class='bg-gray-900 text-gray-100 rounded-lg p-4 overflow-auto my-4'><code>{d.get('code','')}</code></pre>"
    if t == "table":
        rows = d.get("content", [])
        head, body = "", ""
        if rows:
            head = "<thead><tr>" + "".join([f"<th class='px-3 py-2 text-left'>{c}</th>" for c in rows[0]]) + "</tr></thead>"
            body_rows = rows[1:] if len(rows) > 1 else []
            body = "<tbody>" + "".join(["<tr>" + "".join([f"<td class='px-3 py-2'>{c}</td>" for c in r]) + "</tr>" for r in body_rows]) + "</tbody>"
        return f"<div class='overflow-x-auto my-4'><table class='min-w-full border divide-y'>{head}{body}</table></div>"
    if t == "image":
        url = d.get("file", {}).get("url") or d.get("url")
        cap = d.get("caption", "")
        alt = d.get("alt", "")
        if not url:
            return ""
        return (
            f"<figure class='my-6'><img src='{url}' alt='{alt}' loading='lazy' class='rounded-xl shadow'/>"
            f"<figcaption class='text-sm text-gray-500 mt-2'>{cap}</figcaption></figure>"
        )
    if t == "delimiter":
        return "<hr class='my-8'/>"
    return ""


@register.filter
def render_editorjs(value):
    try:
        data = value if isinstance(value, dict) else json.loads(value or "{}")
    except Exception:
        return ""
    blocks = data.get("blocks", [])
    html = "".join(_render_block(b) for b in blocks)
    if bleach:
        tags = getattr(settings, "BLEACH_ALLOWED_TAGS", None)
        attrs = getattr(settings, "BLEACH_ALLOWED_ATTRIBUTES", None)
        protos = getattr(settings, "BLEACH_ALLOWED_PROTOCOLS", None)
        html = bleach.clean(html, tags=tags, attributes=attrs, protocols=protos, strip=False)
    return mark_safe(html)

