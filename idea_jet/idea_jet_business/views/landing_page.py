from typing import Any, Dict
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class LandingPageView(LoginRequiredMixin, TemplateView):
    template_name = 'idea_jet_business/index.html'
    login_url = reverse_lazy('login')  # assuming 'login' is the name of your login url

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["app_url"] = settings.APP_URL
        return context

class LoginView(LoginView):
    template_name = 'idea_jet_business/login.html'
    redirect_authenticated_user = True  # If the user is authenticated, they'll be redirected to 'LOGIN_REDIRECT_URL'