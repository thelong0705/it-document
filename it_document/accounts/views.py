from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from el_pagination.decorators import page_template
from accounts.forms import UserCreateForm, UserLoginForm
from document.models import ActivityLog, Document
from .models import UserProfileInfo

token_generator = PasswordResetTokenGenerator()


class UserDetail(DetailView):
    model = UserProfileInfo
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_profile'


class UpdateUserProfile(UpdateView):
    model = UserProfileInfo
    fields = ('avatar', 'biography')
    template_name = 'accounts/user_update.html'

    def render_to_response(self, context, **response_kwargs):
        if self.object.user != self.request.user:
            return HttpResponseRedirect(reverse('no_permission'))
        return super(UpdateUserProfile, self).render_to_response(context, **response_kwargs)


class NoPermissionView(TemplateView):
    template_name = 'accounts/no_permission.html'


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    form = UserLoginForm()
    if request.method != 'POST':
        return render(request, 'accounts/login.html', {'form': form})
    form = UserLoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is None:
            form.add_error(None, "Username or Password is incorrect!")
            return render(request, 'accounts/login.html', {'form': form})
        login(request, user)
    else:
        return render(request, 'accounts/login.html', {'form': form})
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return HttpResponseRedirect(reverse('index'))


@page_template('accounts/activity_log_page.html')
def user_detail(request, pk, template='accounts/user_detail.html', extra_context=None):
    user_profile = UserProfileInfo.objects.get(pk=pk)
    context = {
        'user_profile': user_profile,
        'logs': ActivityLog.objects.filter(user=user_profile.user).order_by('-time')
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template, context)


@login_required()
@page_template('accounts/activity_log_page.html')
@page_template('accounts/unapprove_documents.html', key='unaprrove_documents_page')
@page_template('accounts/approve_documents.html', key='aprrove_documents_page')
def show_adminpage(request, pk, template='accounts/admin_page.html', extra_context=None):
    user_profile = UserProfileInfo.objects.get(pk=pk)
    if not request.user.is_superuser:
        return render(request, 'accounts/no_permission.html')
    context = {
        'user_profile': user_profile,
        'logs': ActivityLog.objects.filter(user=user_profile.user).order_by('-time'),
        'documents': Document.objects.all().filter(approve=False).order_by('-id'),
        'approve_documents': Document.objects.all().filter(approve=True).order_by('-id')
    }
    if extra_context is not None:
        context.update(extra_context)
    if request.method == 'POST':
        action = request.POST.get('action')
        action_approved = request.POST.get('action-approved')
        if action:
            checkbox = request.POST.getlist('checkbox')
            documents = Document.objects.filter(id__in=checkbox)
            if not checkbox:
                context['no_selected'] = True
                return render(request, template, context=context)
            if action == 'Delete':
                documents.delete()
                context['deleted'] = True
                return render(request, template, context=context)
            else:
                documents.update(approve=True)
                activites = []
                for doc in documents:
                    activites.append(ActivityLog(user=request.user, document=doc, verb='approved'))
                ActivityLog.objects.bulk_create(activites)
                context['approved'] = True
                return render(request, template, context=context)
        else:
            checkbox_approve = request.POST.getlist('checkbox-approve')
            if not checkbox_approve:
                context['no_selected_approve'] = True
                return render(request, template, context=context)
            documents = Document.objects.filter(id__in=checkbox_approve)
            if action_approved == 'Unapprove selected':
                documents.update(approve=False)
                activites = []
                for doc in documents:
                    activites.append(ActivityLog(user=request.user, document=doc, verb='unapproved'))
                ActivityLog.objects.bulk_create(activites)
                context['unapproved'] = True
            else:
                for doc in documents:
                    doc.delete()
                context['deleted_approve'] = True
                return render(request, template, context=context)
    return render(request, template, context=context)


def send_email(request, user, email):
    current_site = get_current_site(request)
    message = render_to_string('accounts/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'pk': user.pk,
        'token': token_generator.make_token(user),
    })
    mail_subject = 'Active your it-document account'
    email_message = EmailMessage(mail_subject, message, to=[email])
    email_message.send()


def sign_up(request):
    resend_email = request.GET.get('resend')
    if resend_email:
        user = get_object_or_404(User, email=resend_email)
        send_email(request, user, resend_email)
        context = {
            'email': resend_email,
            'resend': True
        }
        return render(request, 'accounts/complete_sign_up.html', context)
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            is_email_exist = User.objects.filter(email=user.email).exists()
            if is_email_exist:
                form.add_error('email', 'This email is already taken!')
                return render(request, 'accounts/register.html', {'form': form})
            user.is_active = False
            user.save()
            email = form.cleaned_data.get('email')
            user_profile = UserProfileInfo(user=user)
            user_profile.save()
            send_email(request, user, email)
            return render(request, 'accounts/complete_sign_up.html', {'email': email})
    else:
        form = UserCreateForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate(request, pk, token):
    user = get_object_or_404(User, pk=pk)
    if token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return HttpResponse('Activation link is invalid!')
