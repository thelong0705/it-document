import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, UpdateView
from el_pagination.decorators import page_template
from rest_framework import status

from .forms import DocumentCreateForm
from .models import Document, Comment, UserRateDocument, ActivityLog, Bookmark


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
    return render(request, 'document/thank_you.html', context=context)


@page_template('document/comment_list.html')
def document_detail(request, pk, template='document/document_detail.html', extra_context=None):
    document = get_object_or_404(Document, pk=pk)
    if not document.approve and request.user.is_superuser:
        return HttpResponseRedirect(reverse('unappove_document_detail', kwargs={'pk': pk}))
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
        'comments': Comment.objects.filter(document=document, user__is_active=True).order_by('-submit_date'),
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


@login_required()
def bookmark(request, pk):
    user = request.user
    document = get_object_or_404(Document, pk=pk)
    if not document.approve:
        return render(request, 'accounts/no_permission.html')
    bookmark_obj, created = Bookmark.objects.get_or_create(user=user, document=document)
    if not created:
        bookmark_obj.delete()
    data = {
        'bookmarked': created
    }
    return JsonResponse(data=data)


@login_required()
@require_http_methods(['POST'])
def rate(request):
    rating = int(request.POST.get('rating'))
    document_id = request.POST.get('document')
    document = get_object_or_404(Document, pk=document_id)
    if rating < 1 or rating > 5:
        return HttpResponse('rating must be in range of 1 to 5', status=status.HTTP_400_BAD_REQUEST)
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
        send_email_notification(request, admin=request.user, document=document, is_approve=True)
    else:
        activity = ActivityLog(user=request.user, document=document, verb='unapproved')
        send_email_notification(request, admin=request.user, document=document, is_approve=False)
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


@login_required()
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


@login_required()
@require_http_methods(['POST'])
def comment(request):
    content = request.POST.get('content')
    document_id = request.POST.get('document')
    document = get_object_or_404(Document, pk=document_id)
    if not document.approve:
        return render(request, 'accounts/no_permission.html', status.HTTP_400_BAD_REQUEST)
    com = Comment(user=request.user, document=document, content=content)
    com.save()
    activity = ActivityLog(
        user=request.user,
        document=document,
        verb='commented',
    )
    activity.save()
    return JsonResponse(data={'id': com.id}, status=status.HTTP_200_OK)


@login_required()
@require_http_methods(['POST'])
def update_comment(request):
    comment_id = request.POST.get('comment_id')
    content = request.POST.get('content')
    if not content:
        return HttpResponse('Invalid content', status=status.HTTP_400_BAD_REQUEST)
    com = get_object_or_404(Comment, id=comment_id)
    com.content = content
    com.is_edited = True
    com.save()
    return JsonResponse(data={}, status=status.HTTP_200_OK)


@login_required()
def delete_comment(request, pk):
    com = get_object_or_404(Comment, pk=pk)
    is_owner_or_admin = request.user.is_superuser or request.user == com.user
    if not is_owner_or_admin:
        return render(request, 'accounts/no_permission.html')
    com.delete()
    return HttpResponseRedirect(reverse('document_detail', kwargs={'pk': com.document.id}))


def send_email_notification(request, admin, document, is_approve):
    current_site = get_current_site(request)
    if is_approve:
        html_to_render = 'document/approve_document_notification.html'
        mail_subject = 'Congratulations your document has been approved'
    else:
        html_to_render = 'document/unapprove_document_notification.html'
        mail_subject = 'Your document has been unapproved'
    message = render_to_string(html_to_render, {
        'user': document.posted_user,
        'admin': admin,
        'domain': current_site.domain,
        'pk': document.pk,
    })
    email_message = EmailMessage(mail_subject, message, to=[document.posted_user.email])
    email_message.send()
