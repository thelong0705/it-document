from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.urls import reverse
from django.views.generic import TemplateView
from el_pagination.decorators import page_template

from category.models import Category
from document.models import Document


class IndexPage(TemplateView):
    template_name = 'index.html'


def search(request, keyword):
    try:
        category = Category.objects.get(name__iexact=keyword)
        return HttpResponseRedirect(reverse('category_detail', kwargs={'pk': category.id}))
    except Category.DoesNotExist:
        return render(request, 'search.html', {'keyword': keyword})


@page_template('document/top_6_likes.html')
@page_template('document/top_6_rating.html', key='top_rating_page')
def entry_index(request, template='index.html', extra_context=None):
    context = {
        'documents': Document.objects.annotate(
            num_likes=Count('liked_by')
        ).order_by('-num_likes')[:12],
        'documents_top_rating': Document.objects.order_by('-rating')[:12],
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)