from rest_framework import serializers

from idea_jet_business.models import BusinessIdea
from idea_jet_business.serializers import ExecutionStepSerializer, FeatureSerializer


class BusinessIdeaSerializer(serializers.ModelSerializer):

    execution_steps = ExecutionStepSerializer(many=True, read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    
    class Meta:
        model = BusinessIdea
        fields = "__all__"