from rest_framework import serializers

from idea_jet_business.models import BusinessGeneration

from idea_jet_business.serializers.business_idea import BusinessIdeaSerializer


class BusinessGenerationSerializer(serializers.ModelSerializer):

    business_ideas = BusinessIdeaSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessGeneration
        fields = "__all__"