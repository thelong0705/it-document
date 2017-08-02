from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from el_pagination.decorators import page_template

from accounts.forms import UserCreateForm, UserLoginForm
from document.models import ActivityLog
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
