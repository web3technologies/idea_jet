from rest_framework import serializers
from idea_jet_business.models import Logo


class LogoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logo
        fields = "__all__"