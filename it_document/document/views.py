from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView


from .forms import DocumentCreateForm


class AddNewDocumentView(LoginRequiredMixin, CreateView):
    form_class = DocumentCreateForm
    template_name = 'document/add_new_document.html'
    success_url = reverse_lazy('thankyou')

    def form_valid(self, form):
        form.instance.posted_user = self.request.user
        return super(AddNewDocumentView, self).form_valid(form)


class ThankYouView(TemplateView):
    template_name = 'document/thank_you.html'

