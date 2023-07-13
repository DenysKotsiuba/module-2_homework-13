from typing import Any
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from .forms import RegisterForm


class RegisterView(View):
    form_class = RegisterForm
    template = "users/signup.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if request.user.is_authenticated:
            return redirect(to='quotes:root')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, messages=None):
        return render(request, self.template, context = {"form": self.form_class})
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            messages.success(request, f"{username}, your account has been successfully created")
            new_user = authenticate(request, username=username, password=password)

            if new_user:
                login(request, new_user)

            return redirect(to="quotes:root")
        
        return render(request, self.template, {"form": form})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    success_message = "An email with instructions to reset your password has been sent to %(email)s."
    subject_template_name = 'users/password_reset_subject.txt' 


