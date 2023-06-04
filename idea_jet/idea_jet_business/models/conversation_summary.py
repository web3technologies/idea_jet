from django.db import models
from django.utils import timezone

from idea_jet_business.models import BusinessIdea


class ConversationSummary(models.Model):
    
    date = models.DateTimeField(default=timezone.now)
    summary = models.TextField()
    type = models.CharField(choices=(("INITIAL", "INITIAL"), ))

    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE)