from django.urls import path, include
from rest_framework import routers

from idea_jet_business.views import BusinessIdeaView, BusinessIdeaViewSet


router = routers.SimpleRouter()
router.register(r'business-ideas', BusinessIdeaViewSet)


urlpatterns = [
    path('generate/', BusinessIdeaView.as_view(), name='business_idea'),
    path('businesses/', include(router.urls))
]