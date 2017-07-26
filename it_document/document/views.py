from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, TemplateView, DetailView, UpdateView, DeleteView
from .models import Document
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


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'document/document_detail.html'
    context_object_name = 'document'


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentCreateForm
    template_name = 'document/document_update.html'

    def render_to_response(self, context, **response_kwargs):
        if self.object.posted_user != self.request.user:
            return HttpResponseRedirect(reverse('no_permission'))
        return super().render_to_response(context, **response_kwargs)

    def get_success_url(self):
        return reverse('document_detail', kwargs={'slug': self.get_object().slug})


class DeleteDocumentView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'document/document_delete.html'
    success_url = reverse_lazy('index')

    def render_to_response(self, context, **response_kwargs):
        if self.object.posted_user != self.request.user:
            return HttpResponseRedirect(reverse('no_permission'))
        return super().render_to_response(context, **response_kwargs)
