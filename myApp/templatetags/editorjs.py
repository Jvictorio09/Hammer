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


def _render_inline_text(text_data):
    """
    Render Editor.js inline text data (can be string or array with inline formatting).
    Editor.js stores text with inline formatting (bold, italic, links) as an array of fragments.
    Also handles cases where HTML is stored directly in the text field.
    """
    if not text_data:
        return ""
    
    # If it's a simple string
    if isinstance(text_data, str):
        # Check if it already contains HTML anchor tags (links saved as HTML)
        if '<a ' in text_data.lower() or '</a>' in text_data.lower():
            # Text contains HTML links - preserve and style them
            # Don't escape - we want to preserve the HTML
            import re
            def add_link_styling(match):
                full_tag = match.group(0)
                # Check if class already exists
                if 'class=' in full_tag:
                    # Add our classes to existing class (avoid duplicates)
                    if 'text-[#18AFAB]' not in full_tag:
                        full_tag = re.sub(r'class="([^"]*)"', r'class="\1 text-[#18AFAB] underline decoration-[#18AFAB]/30 hover:decoration-[#18AFAB] hover:text-[#159d99] font-medium transition-all"', full_tag)
                else:
                    # Add class attribute
                    full_tag = full_tag.replace('<a ', '<a class="text-[#18AFAB] underline decoration-[#18AFAB]/30 hover:decoration-[#18AFAB] hover:text-[#159d99] font-medium transition-all" ')
                # Ensure target and rel attributes
                if 'target=' not in full_tag:
                    full_tag = full_tag.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ')
                elif 'target="_blank"' not in full_tag:
                    # Has target but not _blank, update it
                    full_tag = re.sub(r'target="[^"]*"', 'target="_blank"', full_tag)
                if 'rel=' not in full_tag:
                    full_tag = full_tag.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')
                return full_tag
            # Apply styling to all anchor tags
            styled_text = re.sub(r'<a\s+[^>]*>', add_link_styling, text_data)
            return styled_text
        else:
            # Plain text - linkify URLs
            return _linkify_text(text_data)
    
    # If it's an array (has inline formatting like links, bold, italic)
    if isinstance(text_data, list):
        html_parts = []
        for fragment in text_data:
            if isinstance(fragment, str):
                html_parts.append(escape(fragment))
            elif isinstance(fragment, dict):
                # Fragment with formatting
                text = fragment.get('text', '')
                escaped_text = escape(text)
                
                # Check for link (Editor.js native format)
                link_data = fragment.get('link')
                if link_data:
                    # Link can be a string (URL) or object with 'url' property
                    url = link_data if isinstance(link_data, str) else link_data.get('url', '')
                    if url:
                        safe_url = url.replace('"', '&quot;').replace("'", '&#x27;')
                        # Check for other formatting
                        if fragment.get('bold'):
                            escaped_text = f'<strong>{escaped_text}</strong>'
                        if fragment.get('italic'):
                            escaped_text = f'<em>{escaped_text}</em>'
                        html_parts.append(f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer" class="text-[#18AFAB] underline decoration-[#18AFAB]/30 hover:decoration-[#18AFAB] hover:text-[#159d99] font-medium transition-all">{escaped_text}</a>')
                    else:
                        # Link data but no URL - just format text
                        if fragment.get('bold'):
                            escaped_text = f'<strong>{escaped_text}</strong>'
                        if fragment.get('italic'):
                            escaped_text = f'<em>{escaped_text}</em>'
                        html_parts.append(escaped_text)
                else:
                    # Just bold/italic, no link
                    if fragment.get('bold'):
                        escaped_text = f'<strong>{escaped_text}</strong>'
                    if fragment.get('italic'):
                        escaped_text = f'<em>{escaped_text}</em>'
                    html_parts.append(escaped_text)
            else:
                html_parts.append(escape(str(fragment)))
        return ''.join(html_parts)
    
    return escape(str(text_data))


def _linkify_text(text):
    """Convert plain URLs in text to clickable HTML links (fallback for plain text)"""
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
        text_data = d.get("text", "")
        rendered_text = _render_inline_text(text_data)
        # If rendered text contains HTML (like links), mark it as safe
        if '<a ' in rendered_text.lower() or '<strong>' in rendered_text.lower() or '<em>' in rendered_text.lower():
            return mark_safe(f'<p class="mb-4">{rendered_text}</p>')
        return f'<p class="mb-4">{rendered_text}</p>'
    if t == "header":
        level = d.get("level", 2)
        text_data = d.get("text", "")
        rendered_text = _render_inline_text(text_data)
        if level == 3:
            return f'<h3 class="text-xl font-semibold mt-6 mb-3">{rendered_text}</h3>'
        return f'<h2 class="text-2xl font-bold mt-8 mb-4">{rendered_text}</h2>'
    if t == "list":
        style = d.get("style", "unordered")
        items = "".join([f"<li>{_render_inline_text(i)}</li>" for i in d.get("items", [])])
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

