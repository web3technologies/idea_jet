from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView

from idea_jet_business.models import BusinessIdea
from idea_jet_business.scripts.idea_gen import BusinessIdeaGeneration
from idea_jet_business.serializers import BusinessIdeaSerializer


class BusinessIdeaView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        business_idea = BusinessIdeaGeneration().run(user_id=self.request.user.id)
        return Response(data=business_idea, status=status.HTTP_201_CREATED)


class BusinessIdeaViewSet(viewsets.ModelViewSet):
    queryset = BusinessIdea.objects.all()
    serializer_class = BusinessIdeaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    # todo make sure only user requesting has access to their business ideas
    def get_object(self):
        return super().get_object()