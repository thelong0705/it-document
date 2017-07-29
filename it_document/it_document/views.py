from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from category.models import Category


class IndexPage(TemplateView):
    template_name = 'index.html'


def search(request, keyword):
    try:
        category = Category.objects.get(name__iexact=keyword)
        return HttpResponseRedirect(reverse('category_detail', kwargs={'pk': category.id}))
    except Category.DoesNotExist:
        return render(request, 'search.html', {'keyword': keyword})
