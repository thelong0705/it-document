from django import template
from document.models import Document

register = template.Library()


@register.inclusion_tag('document/top_likes.html')
def get_top_likes_list():
    return {'documents': Document.objects.order_by('-number_of_likes')[:6]}


@register.inclusion_tag('document/top_likes.html')
def get_top_views_list():
    return {'documents': Document.objects.order_by('-number_of_views')[:6]}
