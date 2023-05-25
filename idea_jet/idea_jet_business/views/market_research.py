from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from idea_jet_business.models import MarketResearch
from idea_jet_business.serializers import MarketResearchSerializer


class MarketResearchViewset(viewsets.ModelViewSet):
    queryset = MarketResearch.objects.all()
    serializer_class = MarketResearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    # todo make sure only user requesting has access to their business ideas
    def get_object(self):
        return super().get_object()
    