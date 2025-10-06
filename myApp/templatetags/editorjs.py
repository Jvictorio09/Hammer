from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
import json

try:
    import bleach  # type: ignore
except Exception:  # pragma: no cover
    bleach = None

register = template.Library()


def _render_block(b):
    t = b.get("type")
    d = b.get("data", {})
    if t == "paragraph":
        return f'<p class="mb-4">{d.get("text","")}</p>'
    if t == "header":
        level = d.get("level", 2)
        text = d.get("text", "")
        if level == 3:
            return f'<h3 class="text-xl font-semibold mt-6 mb-3">{text}</h3>'
        return f'<h2 class="text-2xl font-bold mt-8 mb-4">{text}</h2>'
    if t == "list":
        style = d.get("style", "unordered")
        items = "".join([f"<li>{i}</li>" for i in d.get("items", [])])
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

