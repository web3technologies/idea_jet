from django.conf import settings
from django.db import models
from django.utils import timezone

from idea_jet_catalog.models import BusinessModelType, IndustryType
from idea_jet_business.models.business_generation import BusinessGeneration


class BusinessIdea(models.Model):
    business_name = models.CharField(max_length=255)
    business_idea = models.TextField()
    date_generated = models.DateTimeField(default=timezone.now)
    product = models.TextField(default="")

    business_generation = models.ForeignKey(
        BusinessGeneration, 
        on_delete=models.DO_NOTHING, 
        default=None, 
        null=True,
        related_name="business_ideas"
    )
    business_model = models.ForeignKey(BusinessModelType, on_delete=models.DO_NOTHING, default=None, null=True)
    industry_type = models.ForeignKey(IndustryType, on_delete=models.DO_NOTHING, default=None, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="business_ideas", 
        null=True,
        default=None
    )
    original_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="original_business_ideas",
        null=True,
        default=None
    )
    