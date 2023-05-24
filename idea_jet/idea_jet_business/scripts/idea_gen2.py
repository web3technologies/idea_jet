from decouple import config
from django.db import transaction
from django.contrib.auth import get_user_model
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import BaseOutputParser, OutputParserException
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from langchain.prompts.chat import (
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    AIMessagePromptTemplate
)
import openai
import pprint

from idea_jet_business.models import BusinessIdea, ExecutionStep, Feature
from idea_jet_catalog.models import BusinessModelType, IndustryType
from idea_jet_business.serializers import BusinessIdeaSerializer


OPEN_API_KEY = config("OPEN_API_KEY")


class BusinessIdeaGenerationV2:

    system_template = """
            You are a very successful entrepreneur. 
            Examples: "Peter thiel", "Elon Musk", "Jeff Bezos"
            You think like them.
            You have created many multi million dollar revenue businesses in the past.
            You have also raised millions of dollars in funding and have exited with multi million dollar exits.
        """
    
    system_template_2 = """
        Your goal is to:
            - Generate a unique business idea
            - Generate a name for this business
            - Generate an array of product features
            - Generate an array of three execution steps
            - Generate a follow up question that can help you gain more context for the business
            {format_instructions}
    """
            # - Generate the business model type for the business based on these business models {business_models}
            # - Generate the industry type the business is in based on these {industry_types}    
    system_prompt = SystemMessagePromptTemplate.from_template(system_template)
    system_prompt_2 = SystemMessagePromptTemplate.from_template(system_template_2)

    def __init__(self) -> None:
        openai.api_key = OPEN_API_KEY
        self.chat_model = ChatOpenAI(temperature=1, model="gpt-3.5-turbo", openai_api_key=OPEN_API_KEY)
        self.industries = list(IndustryType.objects.all().values_list("industry_type", flat=True))
        self.business_models = list(BusinessModelType.objects.all().values_list("business_model_type", flat=True))
        self.user_model = get_user_model()
        self.messages = []
        self.response_schemas = [
                ResponseSchema(name="business_name", description="This is the name of the business you have generated"),
                ResponseSchema(name="business_idea", description="This is the business idea you will generate"),
                ResponseSchema(name="features", description="This is the array of product features you will generate"),
                ResponseSchema(name="execution_steps", description="This is the array of three execution steps you will generate"),
                ResponseSchema(name="follow_up_question", description="This is the follow up question you will generate"),
                # ResponseSchema(name="business_model", description="This is the business model type for the business you will generate"),
                # ResponseSchema(name="industry_type", description="This is the industry type the business is in will generate"),
            ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)

    @property
    def idea_generation_mapping(self):

        return {
            "random": self._generate_random_idea,
            "custom": self._generate_input_idea,
            "existing": self._generate_user_idea
        }

    def _generate_random_idea(self, *args):
        human_template = """
                Generate a random and unique business
            """
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate(
            messages=[self.system_prompt, human_prompt, self.system_prompt_2],
            input_variables=[],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        business_query = chat_prompt.format_prompt().to_messages()
        return business_query
        
    def _generate_input_idea(self, data: dict):
        human_template = """
                I am providing you a set of inputs that I want you to tailor the idea to: 
                - I have skills in: {skills}
                - I have a budget of: {budget}
            """
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate(
            messages=[self.system_prompt, human_prompt, self.system_prompt_2],
            input_variables=["skills", "budget"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        business_query = chat_prompt.format_prompt(
            skills=data.get("skills"), 
            budget=data.get("budget")
            )
        return business_query.to_messages()
    
    def _generate_user_idea(self, data: dict):
        human_template = """
                I have this business idea: {existingIdea}
                Use this idea to create a unique business
            """
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate(
            messages=[self.system_prompt, human_prompt, self.system_prompt_2],
            input_variables=["existingIdea"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        business_query = chat_prompt.format_prompt(existingIdea=data.get("existingIdea"))
        return business_query.to_messages()
        
    def run(self, user_id, action, data):

        with transaction.atomic():

            business_query = self.idea_generation_mapping[action](data)
            self.messages.extend(business_query)

            print(f"generating {action} idea ... \n")
            business_output = self.chat_model(self.messages)
            print(business_output)
            print()
            try:
                business_output = self.output_parser.parse(business_output.content)
            except OutputParserException as e:
                print("json error attempting to fix")
                # catch the exception for the json output and tell chat gpt to correct the json
                self.messages.append(HumanMessage(content="You outputed incorrect json as described earlier. Fix this and output correct json."))
                business_output = self.chat_model(self.messages)
                business_output = self.output_parser.parse(business_output.content)

            pprint.pprint(business_output)
            # self.messages.append(HumanMessage(content="Summarize this entire conversation"))
            # ai_response = self.chat_model(self.messages)
            # self.messages.append(ai_response)
            # print(ai_response)
            print("creating objects")
            try:
                b_idea = BusinessIdea.objects.create(
                    business_name=business_output["business_name"],
                    business_idea=business_output["business_idea"],
                    # business_model=BusinessModelType.objects.get(business_model_type=business_output["business_model"]),
                    # industry_type=IndustryType.objects.get(industry_type=business_output["industry_type"]),
                    user=self.user_model.objects.get(id=user_id)
                )
            except (BusinessModelType.DoesNotExist, IndustryType.DoesNotExist) as e:
                print(business_output["business_model"])
                print(business_output["industry_type"])
                raise e
            
            features_to_create = [
                Feature(
                    feature=feature,
                    business_idea=b_idea
                )
                for feature in business_output.get("features")
            ]
            execution_steps_to_create = [
                ExecutionStep(
                    execution_step=execution_step,
                    business_idea=b_idea
                )
                for execution_step in business_output.get("execution_steps")
            ]
            Feature.objects.bulk_create(features_to_create)
            ExecutionStep.objects.bulk_create(execution_steps_to_create)

        return BusinessIdeaSerializer(b_idea).data
        



    