from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^thank/$', views.ThankYouView.as_view(), name='thankyou'),
    url(r'^add/$', views.AddNewDocumentView.as_view(), name='add_doc'),
]


