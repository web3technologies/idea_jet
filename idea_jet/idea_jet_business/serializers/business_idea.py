from rest_framework import serializers
from idea_jet_business.models import BusinessIdea


class BusinessIdeaSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessIdea
        fields = "__all__"