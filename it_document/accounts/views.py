from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import DetailView, UpdateView, TemplateView
from el_pagination.decorators import page_template

from accounts.forms import UserCreateForm, UserLoginForm, ForgotPasswordForm, ChangePasswordForm
from document.models import ActivityLog, Document
from .models import UserProfileInfo

token_generator = PasswordResetTokenGenerator()


class UserDetail(DetailView):
    model = UserProfileInfo
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_profile'


class UpdateUserProfile(LoginRequiredMixin, UpdateView):
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
        username = request.GET.get('username')
        if username:
            print(username)
            context = {
                'form': form,
                'username': username
            }
            return render(request, 'accounts/login.html', context=context)
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
                activites = (
                    ActivityLog(user=request.user, document=doc, verb='approved') for doc in documents
                )
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
                activites = (
                    ActivityLog(user=request.user, document=doc, verb='unapproved') for doc in documents
                )
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


def send_email_change_pass(request, user, email):
    current_site = get_current_site(request)
    message = render_to_string('accounts/acc_change_password_email.html', {
        'user': user,
        'domain': current_site.domain,
        'pk': user.pk,
        'token': token_generator.make_token(user),
    })
    mail_subject = 'Change your IT-Document account password'
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


def forgot_pass(request):
    resend_email = request.GET.get('resend')
    if resend_email:
        user = get_object_or_404(User, email=resend_email)
        send_email_change_pass(request, user, resend_email)
        context = {
            'email': resend_email,
            'resend': True
        }
        return render(request, 'accounts/complete_change_pass.html', context)
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            if not username and not email:
                form.add_error(None, 'Email or username must be filled')
                return render(request, 'accounts/forgot_password_form.html', {'form': form})
            if username and email:
                user = User.objects.get(username=username)
                if user.email != email:
                    form.add_error(None, 'Email and username doesnt match')
                    return render(request, 'accounts/forgot_password_form.html', {'form': form})
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    form.add_error('username', 'This user isnt exist')
                    return render(request, 'accounts/forgot_password_form.html', {'form': form})
                send_email_change_pass(request, user, user.email)
                return render(request, 'accounts/complete_change_pass.html', {'email': user.email})
            if email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    form.add_error('email', 'This email doensnt match with any user')
                    return render(request, 'accounts/forgot_password_form.html', {'form': form})
                send_email_change_pass(request, user, user.email)
                return render(request, 'accounts/complete_change_pass.html', {'email': user.email})
    else:
        form = ForgotPasswordForm()
        return render(request, 'accounts/forgot_password_form.html', {'form': form})


def change_pass(request, pk, token):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 != password2:
                form.add_error(None, 'Password confirm doesnt match')
                return render(request, 'accounts/change_password_form.html', {'form': form})
            user.set_password(password1)
            user.save()
            return HttpResponseRedirect('/accounts/login/?username={}'.format(user.username))
    else:
        if token_generator.check_token(user, token):
            form = ChangePasswordForm()
            return render(request, 'accounts/change_password_form.html', {'form': form})
    return HttpResponse('Change password link is invalid!')
