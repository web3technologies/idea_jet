from .generator_tasks import *


_generator_tasks = [
    generate_business_idea_task, 
    generate_competitor_analysis_task,
    generate_market_research_task
]

__all__ = [
    *_generator_tasks
]