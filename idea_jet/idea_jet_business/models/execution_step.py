from django.db import models

from idea_jet_business.models import BusinessIdea


class ExecutionStep(models.Model):

    execution_step = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name="execution_steps")