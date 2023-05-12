from django.conf import settings
from django.db import models


class BusinessIdea(models.Model):
    busines_name = models.CharField(max_length=255)
    business_idea = models.TextField()
    pricing_model = models.TextField()
    finance_model = models.TextField()
    marketing_strategy = models.TextField()
    white_paper = models.TextField()
    date_generated = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to="business_ideas")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    