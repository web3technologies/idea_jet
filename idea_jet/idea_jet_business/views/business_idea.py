from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView


from idea_jet_business.models import BusinessIdea
from idea_jet_business.generation import (
    BusinessIdeaGenerationV2, 
    CompetitorAnalysisGenerator, 
    MarketResearchGenerator
)
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
    
    @action(
        detail=False,
        methods=["post"],
        url_path="save",
        name="save_business_idea",
    )
    def save_idea(self, request, *args, **kwargs):
        b_idea = BusinessIdea.objects.get(id=self.request.data.get("id"))
        b_idea.user = self.request.user
        b_idea.save(update_fields=["user"])
        # researcher = MarketResearchGenerator()
        # researcher.run(business_id=b_idea.id)
        competitive_analysis = CompetitorAnalysisGenerator()
        competitive_analysis.run(business_id=b_idea.id)
        return Response(data={"detail": 'saved'}, status=status.HTTP_202_ACCEPTED)