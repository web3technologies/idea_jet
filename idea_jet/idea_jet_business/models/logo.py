from django.db import models
from django.utils import timezone

from idea_jet_business.models import BusinessIdea


class Logo(models.Model):

    file = models.ImageField(upload_to="logos")
    date = models.DateTimeField(default=timezone.now)
    is_selected = models.BooleanField(default=False)
    
    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name="logos")
