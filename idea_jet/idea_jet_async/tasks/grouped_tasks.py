from celery import shared_task, group 

from idea_jet_async.tasks.base import BaseCeleryTask
from idea_jet_async.tasks import generate_competitor_analysis_task, generate_market_research_task


@shared_task(bind=True, name="generate_business_idea_metadata_task", base=BaseCeleryTask)
def generate_business_idea_metadata_task(self, business_idea_id, *args, **kwargs):
    networth_calculations = group(
        [
            generate_competitor_analysis_task.s(business_idea_id), 
            generate_market_research_task.s(business_idea_id)
        ]
    )
    return networth_calculations.apply_async()