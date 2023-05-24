from django.db import models

from idea_jet_business.models import BusinessIdea


class Feature(models.Model):

    feature = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name="features")
