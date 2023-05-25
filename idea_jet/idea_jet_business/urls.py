from django.urls import path, include
from rest_framework import routers

from idea_jet_business.views import BusinessIdeaView, BusinessIdeaViewSet, MarketResearchViewset


router = routers.SimpleRouter()
router.register(r'business-ideas', BusinessIdeaViewSet)
router.register(r"market-research", MarketResearchViewset)


urlpatterns = [
    path('generate/', BusinessIdeaView.as_view(), name='business_idea'),
    path('businesses/', include(router.urls))
]