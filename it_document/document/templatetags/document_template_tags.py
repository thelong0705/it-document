from django import template
from django.contrib.auth.models import User
from django.db.models import Count

from document.models import Document, Comment, Bookmark
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
            ).order_by('-num_likes').exclude(approve=False)[:6]
        )
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
        ).order_by('-num_likes', '-rating').exclude(approve=False)[:6]
    }


@register.inclusion_tag('document/top_likes.html')
def get_document_search(keyword):
    return {
        'documents': Document.objects.filter(title__icontains=keyword).exclude(approve=False)
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


@register.inclusion_tag('document/top_likes.html')
def get_documents_by_user(user):
    return {
        'documents': Document.objects.filter(posted_user=user).exclude(approve=False)
    }


@register.inclusion_tag('document/top_likes.html')
def get_unapprove_documents_by_user(user):
    return {
        'documents': Document.objects.filter(posted_user=user).filter(approve=False)
    }


@register.inclusion_tag('document/top_likes.html')
def get_bookmark_documents(user):
    return {
        'documents': Document.objects.filter(bookmark__user=user)
    }
