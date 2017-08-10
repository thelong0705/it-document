from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^thank/(?P<pk>\d+)/$', views.thank_you, name='thankyou'),
    url(r'^add/$', views.AddNewDocumentView.as_view(), name='add_doc'),
    url(r'^detail/(?P<pk>\d+)/$', views.document_detail, name='document_detail'),
    url(r'^detail/unapprove/(?P<pk>\d+)/$', views.unapprove_document_detail, name='unappove_document_detail'),
    url(r'^update/(?P<pk>\d+)/$', views.DocumentUpdateView.as_view(), name='document_update'),
    url(r'^delete/api/(?P<pk>\d+)/$', views.delete_document, name='document_delete_api'),
    url(r'^like/(?P<pk>\d+)/$', views.like, name='document_like'),
    url(r'^bookmark/(?P<pk>\d+)/$', views.bookmark, name='document_bookmark'),
    url(r'^approve/(?P<pk>\d+)/$', views.approve, name='document_approve'),
    url(r'^rate/$', views.rate, name='document_rate'),
    url(r'^download/(?P<path>.*)/$', views.download, name='download'),
    url(r'api/comment/$', views.comment, name='comment'),
    url(r'api/update-comment/$', views.update_comment, name='update_comment'),
    url(r'comment/delete/(?P<pk>\d+)/$', views.delete_comment, name='delete_comment')
]
