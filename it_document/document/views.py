import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Avg
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, TemplateView, DetailView, UpdateView, DeleteView
from rest_framework import authentication, permissions, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.routers import DefaultRouter
from .models import Document, Comment, UserRateDocument, ActivityLog, Bookmark
from .forms import DocumentCreateForm
from rest_framework import viewsets, serializers
from el_pagination.decorators import page_template
from el_pagination.views import AjaxListView


class AddNewDocumentView(LoginRequiredMixin, CreateView):
    form_class = DocumentCreateForm
    template_name = 'document/add_new_document.html'

    def form_valid(self, form):
        form.instance.posted_user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('thankyou', kwargs={'pk': self.object.id})


def thank_you(request, pk):
    context = {'pk': pk}
    return render(request, 'document/thank_you.html',context=context)


@page_template('document/comment_list.html')
def document_detail(request, pk, template='document/document_detail.html', extra_context=None):
    document = get_object_or_404(Document, pk=pk)
    if not document.approve:
        return render(request, 'accounts/no_permission.html')
    liked = document.liked_by.all().filter(id=request.user.id).exists()
    if request.user.is_authenticated:
        bookmarked = Bookmark.objects.filter(user=request.user, document=document).exists()
    else:
        bookmarked = False
    try:
        rated = document.userratedocument_set.get(user__username=request.user).rating
    except UserRateDocument.DoesNotExist:
        rated = -1
    context = {
        'document': document,
        'comments': Comment.objects.filter(document=document).order_by('-submit_date'),
        'rating': document.userratedocument_set.all().aggregate(Avg('rating'))['rating__avg'],
        'number_of_rate': document.userratedocument_set.all().count(),
        'rated': rated,
        'liked': liked,
        'bookmarked': bookmarked
    }

    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentCreateForm
    template_name = 'document/document_update.html'

    def render_to_response(self, context, **response_kwargs):
        if self.object.posted_user != self.request.user:
            return HttpResponseRedirect(reverse('no_permission'))
        return super().render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        activity = ActivityLog(user=self.object.posted_user, document=self.object, verb='edited')
        activity.save()
        self.object.update_date()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_detail', kwargs={'pk': self.get_object().id})


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('user', 'document', 'content')


class NewPostCommentAPI(viewsets.GenericViewSet, ListCreateAPIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = CommentSerializer


router = DefaultRouter()
router.register('comment', NewPostCommentAPI, base_name='CommentAPI')
urlpatterns = router.urls


@login_required()
def like(request, pk):
    user = request.user
    document = get_object_or_404(Document, pk=pk)
    if not document.approve:
        return render(request, 'accounts/no_permission.html')
    if user in document.liked_by.all():
        document.liked_by.remove(user)
        activity = ActivityLog(user=user, document=document, verb='unliked')
        activity.save()
        is_like = False
    else:
        document.liked_by.add(user)
        is_like = True
        activity = ActivityLog(user=user, document=document, verb='liked')
        activity.save()
    data = {
        "is_like": is_like,
        "num_likes": document.liked_by.count()
    }
    return JsonResponse(data=data)


def bookmark(request,pk):
    user = request.user
    document = get_object_or_404(Document, pk=pk)
    if not document.approve:
        return render(request, 'accounts/no_permission.html')
    bookmark_obj, created = Bookmark.objects.get_or_create(user=user,document=document)
    if not created:
        bookmark_obj.delete()
    data = {
        'bookmarked': created
    }
    return JsonResponse(data=data)


@login_required()
@require_http_methods(['POST'])
def rate(request):
    rating = request.POST.get('rating')
    document_id = request.POST.get('document')
    document = get_object_or_404(Document, pk=document_id)
    if not document.approve:
        return render(request, 'accounts/no_permission.html')
    rating_obj, created = UserRateDocument.objects.get_or_create(
        user=request.user, document=document, defaults={'rating': rating}
    )
    if not created:
        rating_obj.rating = rating
        rating_obj.save()
    document.rating = document.userratedocument_set.all().aggregate(Avg('rating'))['rating__avg']
    document.save()
    activity = ActivityLog(
        user=request.user,
        document=document,
        verb='rated',
        content='{} stars'.format(rating)
    )
    activity.save()
    data = {
        'rate_avg': document.userratedocument_set.all().aggregate(Avg('rating'))['rating__avg'],
        'number_of_votes': document.userratedocument_set.all().count()
    }
    return JsonResponse(data=data)


@login_required()
def approve(request, pk):
    if not request.user.is_superuser:
        return render(request, 'accounts/no_permission.html')
    document = get_object_or_404(Document, pk=pk)
    document.approve = not document.approve
    document.save()
    if document.approve:
        activity = ActivityLog(user=request.user, document=document, verb='approved')
    else:
        activity = ActivityLog(user=request.user, document=document, verb='unapproved')
    activity.save()
    data = {
        'is_approve': document.approve
    }
    return JsonResponse(data=data)


def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename={}'.format((os.path.basename(file_path)))
            return response
    raise Http404


def unapprove_document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    is_owner_or_admin = request.user.is_superuser or request.user == document.posted_user
    if not is_owner_or_admin:
        return render(request, 'accounts/no_permission.html')

    context = {
        'document': document,
        'is_approve': document.approve
    }
    return render(request, 'document/unapprove_document_detail.html', context=context)


@login_required()
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    is_owner_or_admin = request.user.is_superuser or request.user == document.posted_user
    if not is_owner_or_admin:
        return render(request, 'accounts/no_permission.html')
    document.delete()
    data = {
        'deleted': True
    }
    return JsonResponse(data=data)
