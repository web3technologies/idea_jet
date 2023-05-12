from django.urls import path, include
from rest_framework import routers

from idea_jet_business.views import BusinessIdeaView, BusinessIdeaViewSet


router = routers.DefaultRouter()
router.register('business-ideas', BusinessIdeaViewSet)


urlpatterns = [
    path('generate/', BusinessIdeaView.as_view(), name='business_idea'),
    path('', include(router.urls))
]