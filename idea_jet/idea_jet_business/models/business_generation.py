from django.conf import settings
from django.db import models



class BusinessGeneration(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="business_generations", 
        null=True,
        default=None
    )
