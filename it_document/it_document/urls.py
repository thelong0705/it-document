from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.IndexPage.as_view(), name='index'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^documents/', include('document.urls')),
    url(r'^categories/', include('category.urls')),
    url(r'^search/(?P<keyword>[-+\w]+)/$', views.search, name='search')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
