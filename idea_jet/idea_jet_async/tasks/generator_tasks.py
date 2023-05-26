from celery import shared_task

from idea_jet_async.tasks.base import BaseCeleryTask
from idea_jet_business.generation import (
    BusinessIdeaGenerationV2,
    CompetitorAnalysisGenerator,
    LogoGenerator, 
    MarketResearchGenerator, 
)


@shared_task(bind=True, name="generate_business_idea_task", base=BaseCeleryTask)
def generate_business_idea_task(self, user_id, action, data, *args, **kwargs):
    return BusinessIdeaGenerationV2().run(user_id=user_id, action=action, data=data)


@shared_task(bind=True, name="generate_competitor_analysis_task", base=BaseCeleryTask)
def generate_competitor_analysis_task(self, business_idea_id, *args, **kwargs):
    return CompetitorAnalysisGenerator().run(business_idea_id)


@shared_task(bind=True, name="generate_logo_task", base=BaseCeleryTask)
def generate_logo_task(self, business_idea_id, n=None, *args, **kwargs):
    return LogoGenerator().run(business_idea_id, n=n)


@shared_task(bind=True, name="generate_market_research_task", base=BaseCeleryTask)
def generate_market_research_task(self, business_idea_id, *args, **kwargs):
    return MarketResearchGenerator().run(business_idea_id)



