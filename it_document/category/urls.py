from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^api/add_category/(?P<category_name>[-\w]+)/$', views.PostCategoryAPI.as_view(), name='add_cat_api'),
    url(r'^detail/(?P<pk>\d+)/$', views.CategoryDetailView.as_view(), name='category_detail'),
    url(r'^all/$', views.CategoryListView.as_view(), name='category_list'),
]


