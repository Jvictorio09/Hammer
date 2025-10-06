from django import template
register = template.Library()

@register.filter
def add_class(field, css):
    # merge with any existing class attrs on the widget
    attrs = field.field.widget.attrs
    existing = attrs.get("class", "")
    attrs["class"] = (existing + " " + css).strip()
    return field.as_widget(attrs=attrs)

@register.filter
def split_string(value, delimiter=','):
    """Split a string by delimiter and return a list"""
    return value.split(delimiter)