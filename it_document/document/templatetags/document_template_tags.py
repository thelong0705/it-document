from django import template
from django.contrib.auth.models import User
from django.db.models import Count

from document.models import Document, Comment
from category.models import Category

register = template.Library()


@register.inclusion_tag('document/top_likes.html')
def get_top_likes_list():
    return {
        'documents': Document.objects.annotate(
            num_likes=Count('liked_by')
        ).order_by('-num_likes')[:6]
    }


@register.inclusion_tag('document/top_likes.html')
def get_top_rating_list():
    return {
        'documents': Document.objects.order_by('-rating')[:6]
    }


@register.inclusion_tag('document/top_likes.html')
def get_document_recommendations(document):
    document_recommendations = Document.objects.filter(
        topic__in=document.topic.all()
    ).exclude(id=document.id)
    return {
        'documents': set(
            document_recommendations.annotate(
                num_likes=Count('liked_by')
            ).order_by('-num_likes')[:5]
        )
    }


@register.inclusion_tag('document/comments.html')
def get_comments(document):
    return {
        'comments': Comment.objects.filter(document=document)
    }


@register.inclusion_tag('document/top_likes.html')
def get_document_in_category(category):
    return {
        'documents': Document.objects.filter(topic__id=category.id)
    }


@register.inclusion_tag('document/top_likes.html')
def get_top_document_in_category(category):
    return {
        'documents': Document.objects.filter(
            topic__id__contains=category.id
        ).annotate(
            num_likes=Count('liked_by')
        ).order_by('-num_likes')[:5]
    }


@register.inclusion_tag('document/top_likes.html')
def get_document_search(keyword):
    return {
        'documents': Document.objects.filter(title__icontains=keyword)
    }


@register.inclusion_tag('document/top_user.html')
def get_user_search(keyword):
    return {
        'users': User.objects.filter(username__icontains=keyword)
    }


@register.inclusion_tag('document/top_user.html')
def get_top_user():
    return {
        'users': User.objects.annotate(num_posts=Count('document')).order_by('-num_posts')[:6]
    }
