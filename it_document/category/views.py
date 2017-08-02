from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from el_pagination.decorators import page_template

from document.models import Document
from .models import Category
from rest_framework import status


@require_http_methods(['POST'])
def create_category(request):
    name = request.POST.get('name')
    if not name:
        return JsonResponse(data={}, status=status.HTTP_400_BAD_REQUEST)
    category, created = Category.objects.get_or_create(name=name)
    if created:
        return JsonResponse({'created': created, 'pk': category.id}, status=200)
    return JsonResponse({'created': created}, status=status.HTTP_200_OK)


def get_all_category_api(request):
    name_list = [cat.name for cat in Category.objects.all()]
    return JsonResponse({'name_list': name_list}, status=status.HTTP_200_OK)


@page_template('category/category_page.html')
def category_list(request, template='category/category_list.html', extra_context=None):
    context = {
        'categories': Category.objects.all()
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)


@page_template('category/list_documents_in_category.html')
def category_detail(request, pk, template='category/category_detail.html', extra_context=None):
    context = {
        'category': Category.objects.get(pk=pk),
        'documents': Document.objects.filter(topic__pk=pk)
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)
