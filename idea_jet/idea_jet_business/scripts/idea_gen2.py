from decouple import config
# from django.db import transaction
# from django.contrib.auth import get_user_model
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate
import openai
import pprint
import requests

# from idea_jet_business.models import BusinessIdea

from idea_jet_business.prompt_templates.business import *


OPEN_API_KEY = config("OPEN_API_KEY")


class BusinessIdeaGenerationV2:


    template = """
        You are a genius entrepreneur.
        You are tasked with creating a unique business based on the users inputs.  

        The user has interests in: {interests}.
        They have skills in: {skills}. 
        They have a budget of: ${budget}
        
        Create a business idea for this user.
        Tailor the business idea to interests, skills, and budget of the user. 
        Only create a business idea that you believe can generate revenue.
    """

    def __init__(self) -> None:
        openai.api_key = OPEN_API_KEY
        self.llm = ChatOpenAI(
                    temperature=1, 
                    openai_api_key=OPEN_API_KEY,
                    model="gpt-3.5-turbo"
                )
        # self.user_model = get_user_model()
        
    def run(self, **kwargs):


        buffer_memory = ConversationBufferMemory()

        idea_prompt = PromptTemplate(
            input_variables=["interests", "skills", "budget"], 
            template=self.template
        )
        
        business_idea_chain = LLMChain(llm=self.llm, prompt=idea_prompt)
        business_idea = business_idea_chain.predict(**kwargs)
        return business_idea
        

if __name__ == "__main__":

    messages = []

    chat_model = ChatOpenAI(temperature=1, model="gpt-3.5-turbo", openai_api_key=OPEN_API_KEY)

    system_template = """
    You are a very successful entrepreneur. 
    Examples: "Peter thiel", "Elon Musk", "Jeff Bezos"
    You think like them.
    You have created many multi million dollar revenue businesses in the past.
    You have also raised millions of dollars in funding and have exited with multi million dollar exits.
    
    Your goal is to:
    - Generate a unique business idea
    - Generate a name for this business
    - Generate an array of product features
    - Generate an array of three actions steps
    - Generate a follow up question that can help you gain more context for the business
    - Generate the business model type for the business
    - Generate the industry type the business is in
        {format_instructions}
    """
    # {format_instructions}
    system_prompt = SystemMessagePromptTemplate.from_template(system_template)

    human_template = """
        They have skills in: {skills}
        They have a budget of: {budget}
    """
    human_prompt = HumanMessagePromptTemplate.from_template(human_template)

    response_schemas = [
        ResponseSchema(name="business_name", description="This is the name of the business you have generated"),
        ResponseSchema(name="business_idea", description="This is the business idea you will generate"),
        ResponseSchema(name="features", description="This is the array of product features you will generate"),
        ResponseSchema(name="action_steps", description="This is the array of three actions steps you will generate"),
        ResponseSchema(name="follow_up_question", description="This is the follow up question you will generate"),
        ResponseSchema(name="business_model", description="This is the business model type for the business you will generate"),
        ResponseSchema(name="industry_type", description="This is the industry type the business is in will generate"),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)


    chat_prompt = ChatPromptTemplate(
        messages=[system_prompt, human_prompt],
        input_variables=["skills", "budget"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()}
    )
    buisiness_query = chat_prompt.format_prompt(skills="sales, marketing", budget="1000")
    messages.extend(buisiness_query.to_messages())
    business_output = chat_model(messages)
    print(business_output)
    print()
    output = output_parser.parse(business_output.content)
    pprint.pprint(output)
    # messages.append(business_output)
    # messages.append(HumanMessage(content="What was the first and last feature you generated?"))
    # ai_response = chat_model(messages)
    # print(ai_response)
    # messages.append(ai_response)
    # messages.append(HumanMessage(content=output["follow_up_question"]))
    # ai_response = chat_model(messages)
    # print(ai_response)
    # messages.append(ai_response)
    # messages.append(HumanMessage(content="Summarize this entire conversation"))
    # ai_response = chat_model(messages)
    # messages.append(ai_response)
    # print(ai_response)
    # messages.append(HumanMessage(content="Based on a score of 1 - 10 score this business idea based on your confidence of it become profitable"))
    # print(chat_model(messages))
    #twitter name available
    #webdomains available