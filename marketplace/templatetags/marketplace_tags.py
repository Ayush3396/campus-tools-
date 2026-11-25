"""
marketplace/templatetags/marketplace_tags.py

Custom template filters for the marketplace app.

To use in a template, add at the top:
    {% load marketplace_tags %}

Then use the filter:
    {{ item.availability|badge_class }}   → returns e.g. "badge-lent-out"
    {{ "lent_out"|to_css_class }}         → returns "lent-out"
"""

from django import template

register = template.Library()


@register.filter
def to_css_class(value):
    """
    Converts a Python value with underscores to a CSS-friendly hyphenated string.
    Example: "lent_out"  → "lent-out"
             "like_new"  → "like-new"
             "available" → "available"
    """
    return str(value).replace('_', '-')


@register.filter
def badge_class(value):
    """
    Returns the full badge CSS class for a model field value.
    Example: {{ item.availability|badge_class }} → "badge-lent-out"
    """
    return 'badge-' + str(value).replace('_', '-')
