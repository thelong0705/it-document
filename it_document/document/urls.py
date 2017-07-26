from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^thank/$', views.ThankYouView.as_view(), name='thankyou'),
    url(r'^add/$', views.AddNewDocumentView.as_view(), name='add_doc'),
    url(r'^detail/(?P<slug>[-\w]+)$', views.DocumentDetailView.as_view(), name='document_detail'),
    url(r'^update/(?P<slug>[-\w]+)$', views.DocumentUpdateView.as_view(), name='document_update'),
    url(r'^delete/(?P<slug>[-\w]+)$', views.DeleteDocumentView.as_view(), name='document_delete'),
    url(r'^add-comment/(?P<slug>[-\w]+)/(?P<content>[-\w]+)$', views.PostCommentAPI.as_view(), name='add_comment'),
]
