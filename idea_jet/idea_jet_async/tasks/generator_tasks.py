from celery import shared_task

from idea_jet_async.tasks.base import BaseCeleryTask
from idea_jet_business.generation import (
    BusinessIdeaGenerationRandom,
    BusinessIdeaGenerationAutoGpt,
    BusinessIdeaGenerationAgent,
    CompetitorAnalysisGenerator,
    LogoGenerator, 
    MarketResearchGenerator, 
)


@shared_task(bind=True, name="generate_random_business_idea_task", base=BaseCeleryTask)
def generate_random_business_idea_task(self, user_id, action, data, generation_id, *args, **kwargs):
    return BusinessIdeaGenerationRandom().run(user_id=user_id, action=action, data=data, generation_id=generation_id)


@shared_task(bind=True, name="generate_business_idea_task_v3", base=BaseCeleryTask)
def generate_business_idea_task_v3(self, user_id, action, data, *args, **kwargs):
    return BusinessIdeaGenerationAutoGpt().run(user_id=user_id, action=action, data=data)


@shared_task(bind=True, name="generate_business_idea_task_v4", base=BaseCeleryTask)
def generate_business_idea_task_v4(self, user_id, action, data, *args, **kwargs):
    return BusinessIdeaGenerationAgent().run(user_id=user_id, action=action, data=data)


@shared_task(bind=True, name="generate_competitor_analysis_task", base=BaseCeleryTask)
def generate_competitor_analysis_task(self, business_idea_id, *args, **kwargs):
    return CompetitorAnalysisGenerator().run(business_idea_id)


@shared_task(bind=True, name="generate_logo_task", base=BaseCeleryTask)
def generate_logo_task(self, business_idea_id, n=None, *args, **kwargs):
    return LogoGenerator().run(business_idea_id, n=n)


@shared_task(bind=True, name="generate_market_research_task", base=BaseCeleryTask)
def generate_market_research_task(self, business_idea_id, *args, **kwargs):
    return MarketResearchGenerator().run(business_idea_id)



