from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^register/$', views.sign_up, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^forgot-pass/$', views.forgot_pass, name='forgot_pass'),
    url(r'^change-pass/(?P<pk>\d+)/(?P<token>.*)/$', views.change_pass, name='change_password'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^detail/(?P<pk>\d+)/$', views.user_detail, name='user_detail'),
    url(r'^update/(?P<pk>\d+)/$', views.UpdateUserProfile.as_view(), name='update_user_detail'),
    url(r'^no-permission/$', views.NoPermissionView.as_view(), name='no_permission'),
    url(r'^admin/(?P<pk>\d+)/$', views.show_adminpage, name='admin_page'),
    url(r'^activate/(?P<pk>\d+)/(?P<token>.*)/$',
        views.activate, name='activate'),
]


