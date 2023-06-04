from celery import shared_task, group, chord

from idea_jet_async.tasks.base import BaseCeleryTask
from idea_jet_async.tasks import (
    generate_random_business_idea_task,
    generate_competitor_analysis_task, 
    generate_logo_task,
    generate_market_research_task,
    generate_product_task
)


@shared_task(bind=True, name="generate_business_idea_metadata_task", base=BaseCeleryTask)
def generate_business_idea_metadata_task(self, business_idea_id, *args, **kwargs):

    logo_group = [generate_logo_task.s(business_idea_id, n=n) for n in range(1,4)]
    business_idea_metadata_group = group(
        [
            generate_competitor_analysis_task.s(business_idea_id), 
            generate_market_research_task.s(business_idea_id),
            generate_product_task.s(business_idea_id)
        ] + logo_group
    )

    return business_idea_metadata_group.apply_async()


@shared_task(bind=True, name="generate_random_business_idea_grouped_task", base=BaseCeleryTask)
def generate_random_business_idea_grouped_task(self, user_id, bus_generation_id, *args, **kwargs):

    business_idea_metadata_group = group(
        [
            generate_random_business_idea_task.s(                
                user_id=user_id,
                generation_id=bus_generation_id
            ) for _ in range(0,4)   # creates 4 tasks
        ]
    )

    return chord(business_idea_metadata_group)(generate_random_business_idea_grouped_task_callback.s(bus_generation_id).set(link_error=['generate_random_business_idea_grouped_task']))


@shared_task(bind=True, name="generate_random_business_idea_grouped_task_callback", base=BaseCeleryTask)
def generate_random_business_idea_grouped_task_callback(self, results, bus_generation_id):
    from idea_jet_business.models import BusinessGeneration
    b_idea = BusinessGeneration.objects.get(id=bus_generation_id)
    b_idea.status = "SUCCESS"
    b_idea.save(update_fields=["status"])
    return f"{b_idea.id} success."


@shared_task(bind=True, name="generate_random_business_idea_error_callback", base=BaseCeleryTask)
def generate_random_business_idea_error_callback(self, exc, bus_generation_id):
    from idea_jet_business.models import BusinessGeneration
    b_idea = BusinessGeneration.objects.get(id=bus_generation_id)
    b_idea.status = "FAILURE"
    b_idea.save(update_fields=["status"])
    return f"{b_idea.id} success."