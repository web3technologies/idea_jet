from django.db import transaction
from decouple import config
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import OutputParserException
from langchain.schema import HumanMessage
from langchain.prompts.chat import (
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
    SystemMessagePromptTemplate
)
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool

from idea_jet_business.models import BusinessIdea, ConversationSummary, ExecutionStep, Feature
from idea_jet_catalog.models import BusinessModelType, IndustryType
from idea_jet_business.serializers import BusinessIdeaSerializer
from idea_jet_business.generation.base import BaseGeneration
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.agents.agent_types import AgentType
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.agents import load_tools

import os
import random


SERP_API_KEY = config("SERP_API_KEY")
OPEN_API_KEY = config("OPEN_API_KEY")


class BusinessIdeaGenerationV4(BaseGeneration):

    industries_l = [
        'FinTech',
        'EdTech',
        'E-commerce',
        'Ride-Sharing',
        'Food Delivery',
        'Telecommunication',
        'Workplace Software',
        'Cloud Data Warehousing',
        'Project Management Software',
        'Robotic Process Automation',
        'Aerospace',
        'Data Analytics',
        'Biotech',
        'Healthtech',
        'Cybersecurity',
        'Artificial Intelligence',
        'Virtual Reality',
        'Blockchain',
        'Gaming',
        'InsurTech',
        'GreenTech',
        'Social Media',
        'On-demand Services',
        'IoT',
        'Augmented Reality'
    ]

    def __init__(self, model="gpt-3.5-turbo") -> None:
        super().__init__(model)
        os.environ["SERPAPI_API_KEY"]=SERP_API_KEY


    def run(self, user_id, action, data):
        conversational_memory = ConversationBufferWindowMemory(
            memory_key='chat_history',
            k=5,
            return_messages=True
        )

        # initialize agent with tools
        agent = initialize_agent(
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            tools=load_tools(["serpapi"]),
            llm=self.chat_model,
            verbose=True,
            max_iterations=3,
            early_stopping_method='generate',
            memory=conversational_memory
        )
        # sys_msg = """Assistant is a successful startup founder.

        # Assistant is capable of creating very successful business ideas.

        # Unfortunately, Assistant's market research information is not up to date. Before generating ideas Assistant always useses its tools to perform market research.

        # Overall, Assistant is a successful entrepreneur but needs to perform search research before generating any ideas.
        # """

        
        # new_prompt = agent.agent.create_prompt(
        #     system_message=sys_msg,
        #     tools=load_tools(["serpapi"])
        # )
        # agent.agent.llm_chain.prompt = new_prompt
        # agent.tools = load_tools(["serpapi"])

        industry = random.choice(self.industries_l) 
        # prompt = (
        #     "Lets think of a solution step by step:" + \
        #     f"I would like you to generate a unique startup idea in the {industry} industry." + \
        #     "Here are the steps I would like you to perform:" + \
        #     f"1. Perform some market research to understand the current market of the {industry} industry." + \
        #     f"2. Then generate a new and unique business idea in the {industry}."
        #     f"3. Generate a list of features for this startup idea."
        # )

        
        res = agent(f"provide 3 pieces of recent industry trends for this industry: {industry}")
        return res



        