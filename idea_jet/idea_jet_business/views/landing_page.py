from typing import Any, Dict
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from idea_jet_business.forms import WaitlistForm


class LandingPageView(LoginRequiredMixin, TemplateView):
    template_name = 'idea_jet_business/index.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["app_url"] = settings.APP_URL
        context['form'] = WaitlistForm()
        return context

    def post(self, request, *args, **kwargs):
        form = WaitlistForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You've been added to the waitlist!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                    
        return redirect('landing_page')



class LoginView(LoginView):
    template_name = 'idea_jet_business/login.html'
    redirect_authenticated_user = True  # If the user is authenticated, they'll be redirected to 'LOGIN_REDIRECT_URL'