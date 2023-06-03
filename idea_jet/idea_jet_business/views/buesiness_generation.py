from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from idea_jet_business.models import BusinessGeneration
from idea_jet_business.serializers import BusinessGenerationSerializer


class BusinessGeneartionViewSet(viewsets.ModelViewSet):
    
    queryset = BusinessGeneration.objects.all()
    serializer_class = BusinessGenerationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    # todo make sure only user requesting has access to their business ideas
    def get_object(self):
        return super().get_object()
    
