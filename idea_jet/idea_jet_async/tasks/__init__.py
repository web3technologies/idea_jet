from .generator_tasks import *
from .grouped_tasks import *


_generator_tasks = [
    generate_random_business_idea_task,
    generate_competitor_analysis_task,
    generate_logo_task,
    generate_market_research_task,
    generate_product_task
]


_grouped_tasks = [
    generate_business_idea_metadata_task,
    generate_random_business_idea_grouped_task
]


__all__ = [
    *_generator_tasks,
    *_grouped_tasks
]