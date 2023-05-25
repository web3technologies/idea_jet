from rest_framework import serializers
from idea_jet_business.models import Competitor


class CompetitorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Competitor
        fields = "__all__"