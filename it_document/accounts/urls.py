from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^detail/(?P<pk>\d+)$', views.UserDetail.as_view(), name='user_detail'),
    url(r'^update/(?P<pk>\d+)$', views.UpdateUserProfile.as_view(), name='update_user_detail'),
    url(r'^no-permission/$', views.NoPermissionView.as_view(), name='no_permission')
]


