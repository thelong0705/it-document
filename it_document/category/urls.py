from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^detail/(?P<pk>\d+)/$', views.category_detail, name='category_detail'),
    url(r'^all/$', views.category_list, name='category_list'),
    url(r'^all/api/$', views.get_all_category_api, name='category_list_api'),
    url(r'^ajax/add-cat/$', views.create_category, name='add_category'),
]


