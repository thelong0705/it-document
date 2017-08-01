from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from document.models import Document
from .models import Category
from rest_framework import status

DOCUMENT_PER_PAGE = 5


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category/category_detail'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_list = Document.objects.filter(topic__id=self.object.id).order_by('submit_date')
        paginator = Paginator(document_list, DOCUMENT_PER_PAGE)
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
