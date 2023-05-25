from rest_framework import serializers
from idea_jet_business.models import MarketResearch


class MarketResearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = MarketResearch
        exclude = ["id", "business_idea"]