from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

from idea_jet_business.models import BusinessIdea


class Competitor(models.Model):

    date = models.DateTimeField(default=timezone.now)

    name = models.CharField(max_length=255)
    overview = models.TextField()
    key_features = ArrayField(models.CharField(max_length=100))
    competitive_advantage = models.TextField()

    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name="competitors")