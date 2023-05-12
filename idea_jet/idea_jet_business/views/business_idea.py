from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from idea_jet_business.scripts.idea_gen import BusinessIdeaGeneration


class BusinessIdeaView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        business_idea = BusinessIdeaGeneration().run()
        # business_idea = {
        #     "test1": "test",
        #     "test2": 'test'
        # }
        return Response(data=business_idea, status=status.HTTP_201_CREATED)
