from django.db import models
from django.utils import timezone

from idea_jet_business.models import BusinessIdea


class ExecutionStep(models.Model):

    execution_step = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name="execution_steps")