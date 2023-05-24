from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView

from idea_jet_business.models import BusinessIdea
from idea_jet_business.scripts.idea_gen2 import BusinessIdeaGenerationV2
from idea_jet_business.serializers import BusinessIdeaSerializer


class BusinessIdeaView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        business_idea_data = BusinessIdeaGenerationV2().run(
            user_id=self.request.user.id,
            action=self.request.data.get("action"),
            data=self.request.data.get("data")
            )
        return Response(data=business_idea_data, status=status.HTTP_201_CREATED)


class BusinessIdeaViewSet(viewsets.ModelViewSet):
    queryset = BusinessIdea.objects.all()
    serializer_class = BusinessIdeaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    # todo make sure only user requesting has access to their business ideas
    def get_object(self):
        return super().get_object()