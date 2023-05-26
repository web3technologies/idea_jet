from rest_framework import serializers

from idea_jet_business.models import BusinessIdea
from idea_jet_business.serializers.competitor import CompetitorSerializer
from idea_jet_business.serializers.execution_step import ExecutionStepSerializer
from idea_jet_business.serializers.feature import FeatureSerializer
from idea_jet_business.serializers.logo import LogoSerializer
from idea_jet_business.serializers.market_research import MarketResearchSerializer



class BusinessIdeaSerializer(serializers.ModelSerializer):

    execution_steps = ExecutionStepSerializer(many=True, read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    marketresearch_set = MarketResearchSerializer(many=True, read_only=True)
    competitors = CompetitorSerializer(many=True, read_only=True)
    logos = LogoSerializer(many=True, read_only=True)

    business_model_type = serializers.SlugRelatedField(
        source="business_model", 
        slug_field='business_model_type', 
        read_only=True
    )
    
    class Meta:
        model = BusinessIdea
        fields = "__all__"