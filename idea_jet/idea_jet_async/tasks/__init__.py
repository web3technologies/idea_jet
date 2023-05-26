from .generator_tasks import *
from .grouped_tasks import *


_generator_tasks = [
    generate_business_idea_task, 
    generate_competitor_analysis_task,
    generate_logo_task,
    generate_market_research_task
]


_grouped_tasks = [
    generate_business_idea_metadata_task
]


__all__ = [
    *_generator_tasks,
    *_grouped_tasks
]