from django import template
from django.db.models import Count
from document.models import Category

register = template.Library()


@register.inclusion_tag('category/popular_categories.html')
def get_popular_categories():
    return {'categories': Category.objects.annotate(num_docs=Count('document')).order_by('-num_docs')[:5]}

