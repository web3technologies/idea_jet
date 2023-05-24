from rest_framework import serializers

from idea_jet_business.models import BusinessIdea
from idea_jet_business.serializers.execution_step import ExecutionStepSerializer
from idea_jet_business.serializers.feature import FeatureSerializer


class BusinessIdeaSerializer(serializers.ModelSerializer):

    execution_steps = ExecutionStepSerializer(many=True, read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    business_model_type = serializers.SlugRelatedField(
        source="business_model", 
        slug_field='business_model_type', 
        read_only=True
    )
    
    class Meta:
        model = BusinessIdea
        fields = "__all__"