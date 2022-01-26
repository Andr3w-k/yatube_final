# from django.shortcuts import render
from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeView
    success_url = reverse_lazy('users:password_change_form')
    template_name = 'users/password_change_form.html'


class PasswordChangeDoneView(PasswordChangeDoneView):
    form_class = PasswordChangeDoneView
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_done.html'


class PasswordResetView(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_confirm.html'


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
