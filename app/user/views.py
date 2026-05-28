from django.urls import reverse_lazy
from django.views.generic import CreateView
from user.forms import UserRegisterForm


class RegisterView(CreateView):
    """Register new user."""

    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")
