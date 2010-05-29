from django import template

register = template.Library()

@register.inclusion_tag('app/render_list.html')
def render_list(places):
    return {'places': places}
