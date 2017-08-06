from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^detail/(?P<pk>\d+)/$', views.user_detail, name='user_detail'),
    url(r'^update/(?P<pk>\d+)/$', views.UpdateUserProfile.as_view(), name='update_user_detail'),
    url(r'^no-permission/$', views.NoPermissionView.as_view(), name='no_permission'),
    url(r'^admin/(?P<pk>\d+)/$', views.show_adminpage, name='admin_page')
]


