from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^api/add_category/(?P<category_name>[-\w]+)/$', views.PostCategoryAPI.as_view(), name='add_cat_api'),
]


