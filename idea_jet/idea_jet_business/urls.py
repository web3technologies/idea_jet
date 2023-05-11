from django.urls import path
from idea_jet_business.views import BusinessIdeaView


urlpatterns = [
    path('generate/', BusinessIdeaView.as_view(), name='business_idea'),
]