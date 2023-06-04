from django.conf import settings
from django.db import models
from django.utils import timezone


class BusinessGeneration(models.Model):

    date = models.DateTimeField(default=timezone.now)
    type = models.CharField()
    status = models.CharField(default="PENDING")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="business_generations", 
        null=True,
        default=None
    )
