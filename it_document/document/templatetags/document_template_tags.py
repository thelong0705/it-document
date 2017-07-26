from django import template
from document.models import Document, Comment
from category.models import Category

register = template.Library()


@register.inclusion_tag('document/top_likes.html')
def get_top_likes_list():
    return {'documents': Document.objects.order_by('-number_of_likes')[:5]}


@register.inclusion_tag('document/top_likes.html')
def get_top_views_list():
    return {'documents': Document.objects.order_by('-number_of_views')[:5]}


@register.inclusion_tag('document/top_likes.html')
def get_document_recommendations(document):
    document_recommendations = Document.objects.filter(topic__in=document.topic.all()).exclude(id=document.id)
    return {'documents': set(document_recommendations.order_by('-number_of_likes')[:5])}


@register.inclusion_tag('document/comments.html')
def get_comments(document):
    return {'comments': Comment.objects.filter(document=document)}
