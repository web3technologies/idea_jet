from django.shortcuts import render
from django.views import View


class LandingPageView(View):
    def get(self, request):
        return render(request, 'idea_jet_business/index.html')