from django.db import models
from django.utils import timezone

from idea_jet_business.models import BusinessIdea


class MarketResearch(models.Model):
    
    date = models.DateTimeField(default=timezone.now)

    target_market=models.TextField()
    market_size=models.TextField()
    pricing_model=models.TextField()
    barriers=models.TextField()
    market_positioning=models.TextField()

    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE)