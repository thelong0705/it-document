from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from el_pagination.decorators import page_template
from rest_framework import status

from document.models import Document
from .models import Category


@login_required()
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
    obj_list = []
    for cat in Category.objects.all():
        obj = {
            'value': cat.name,
            'url': '/categories/detail/{}'.format(cat.id),
            'des': '(Category)'
        }
        obj_list.append(obj)
    if request.user.is_superuser:
        for user in User.objects.all():
            obj = {
                'value': user.username,
                'url': '/accounts/detail/{}'.format(user.userprofileinfo.id),
                'des': '(User)'
            }
            obj_list.append(obj)
    else:
        for user in User.objects.filter(is_active=True):
            obj = {
                'value': user.username,
                'url': '/accounts/detail/{}'.format(user.userprofileinfo.id),
                'des': '(User)'
            }
            obj_list.append(obj)
    for doc in Document.objects.filter(approve=True):
        obj = {
            'value': doc.title,
            'url': '/documents/detail/{}'.format(doc.id),
            'des': '(Document)'
        }
        obj_list.append(obj)
    return JsonResponse({'obj_list': obj_list}, status=status.HTTP_200_OK)


@page_template('category/category_page.html')
def category_list(request, template='category/category_list.html', extra_context=None):
    user_filter = request.GET.get('order', '')
    if user_filter == 'Latest':
        context = {
            'categories': Category.objects.all().order_by('-id'),
            'selected': '?order=Latest'
        }
    elif user_filter == 'Documents':
        context = {
            'categories': Category.objects.annotate(
                num_docs=Count('document')
            ).order_by('-num_docs'),
            'selected': '?order=Documents'
        }
    else:
        context = {
            'categories': Category.objects.all().order_by('name'),
            'selected': '?order=Alphabet'
        }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)


@page_template('category/list_documents_in_category.html')
def category_detail(request, pk,
                    template='category/category_detail.html',
                    extra_context=None):
    user_filter = request.GET.get('order', '')
    if user_filter == 'Likes':
        context = {
            'category': Category.objects.get(pk=pk),
            'documents': Document.objects.filter(topic__pk=pk, approve=True).annotate(
                num_likes=Count('liked_by')
            ).order_by('-num_likes', '-rating'),
            'selected': '?order=Likes'
        }
    elif user_filter == 'Rating':
        context = {
            'category': Category.objects.get(pk=pk),
            'documents': Document.objects.annotate(
                num_votes=Count('userratedocument')
            ).filter(approve=True).order_by('-rating', '-num_votes'),
            'selected': '?order=Rating'
        }
    else:
        context = {
            'category': Category.objects.get(pk=pk),
            'documents': Document.objects.filter(topic__pk=pk, approve=True).order_by('-id'),
            'selected': '?order=Date'
        }
        if extra_context is not None:
            context.update(extra_context)
    return render(request, template, context)
