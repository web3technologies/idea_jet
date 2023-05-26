from celery import shared_task, group 

from idea_jet_async.tasks.base import BaseCeleryTask
from idea_jet_async.tasks import (
    generate_competitor_analysis_task, 
    generate_logo_task,
    generate_market_research_task
)


@shared_task(bind=True, name="generate_business_idea_metadata_task", base=BaseCeleryTask)
def generate_business_idea_metadata_task(self, business_idea_id, *args, **kwargs):

    logo_group = [generate_logo_task.s(business_idea_id, n=n) for n in range(1,4)]
    business_idea_metadata_group = group(
        [
            generate_competitor_analysis_task.s(business_idea_id), 
            generate_market_research_task.s(business_idea_id)
        ] + logo_group
    )

    return business_idea_metadata_group.apply_async()