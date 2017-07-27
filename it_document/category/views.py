from django.shortcuts import render
from django.views.generic import DetailView, ListView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from document.models import Document
from .models import Category
from it_document.utils import unslugify


class PostCategoryAPI(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, category_name):
        if category_name == '' or category_name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        category_name = unslugify(category_name)
        obj, created = Category.objects.get_or_create(name=category_name)
        data = {
            "created": created,
            "pk": obj.pk
        }
        return Response(data=data)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category/category_detail'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_list = Document.objects.filter(topic__id__contains=self.object.id).order_by('submit_date')
        paginator = Paginator(document_list, 1)
        page = self.request.GET.get('page')
        try:
            document_list = paginator.page(page)
        except PageNotAnInteger:
            document_list = paginator.page(1)
        except EmptyPage:
            document_list = paginator.page(paginator.num_pages)
        context['document_list'] = document_list
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'category/category_list.html'
    context_object_name = 'category_list'
