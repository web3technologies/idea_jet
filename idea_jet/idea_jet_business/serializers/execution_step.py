from rest_framework import serializers
from idea_jet_business.models import ExecutionStep


class ExecutionStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExecutionStep
        fields = "__all__"