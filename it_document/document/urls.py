from django.conf import settings
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^thank/$', views.ThankYouView.as_view(), name='thankyou'),
    url(r'^add/$', views.AddNewDocumentView.as_view(), name='add_doc'),
    url(r'^detail/(?P<pk>\d+)$', views.DocumentDetailView.as_view(), name='document_detail'),
    url(r'^update/(?P<pk>\d+)$', views.DocumentUpdateView.as_view(), name='document_update'),
    url(r'^delete/(?P<pk>\d+)$', views.DeleteDocumentView.as_view(), name='document_delete'),
    url(r'^like/(?P<pk>\d+)$', views.like, name='document_like'),
    url(r'^rate/$', views.rate, name='document_rate'),
    url(r'^api/', include(views.router.urls, namespace='api')),
    url(r'^download/(?P<path>.*)$', views.download, name='download')
]
