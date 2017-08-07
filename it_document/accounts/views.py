from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from el_pagination.decorators import page_template

from accounts.forms import UserCreateForm, UserLoginForm
from document.models import ActivityLog, Document
from .models import UserProfileInfo


class RegisterView(CreateView):
    form_class = UserCreateForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        user_profile = UserProfileInfo(user=user)
        user_profile.save()
        return super(RegisterView, self).form_valid(form)


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
        print(request.POST.get('action-approved'))
        if action:
            checkbox = request.POST.getlist('checkbox')
            documents = Document.objects.filter(id__in=checkbox)
            if not checkbox:
                context['no_selected'] = True
                return render(request, template, context=context)
            if action == 'Delete':
                for doc in documents:
                    doc.delete()
                context['deleted'] = True
                return render(request, template, context=context)
            else:
                documents.update(approve=True)
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
                context['unapproved'] = True
            else:
                for doc in documents:
                    doc.delete()
                context['deleted_approve'] = True
                return render(request, template, context=context)
    return render(request, template, context=context)
