from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from accounts.forms import UserCreateForm
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
    model = User
    template_name = 'accounts/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.object)
        context['user_profile'] = UserProfileInfo.objects.get(user=self.object)
        return context


class UpdateUserProfile(UpdateView):
    model = UserProfileInfo
    fields = ('avatar', 'biography')
    template_name = 'accounts/user_update.html'
