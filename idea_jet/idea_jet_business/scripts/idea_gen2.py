from decouple import config
from django.db import transaction
from django.contrib.auth import get_user_model
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
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
            
            Your goal is to:
            - Generate a unique business idea
            - Generate a name for this business
            - Generate an array of product features
            - Generate an array of three execution steps
            - Generate a follow up question that can help you gain more context for the business
            - Generate the business model type for the business based on these business models {business_models}
            - Generate the industry type the business is in based on these {industry_types}
                {format_instructions}
        """
    
    system_prompt = SystemMessagePromptTemplate.from_template(system_template)

    def __init__(self) -> None:
        openai.api_key = OPEN_API_KEY
        self.chat_model = ChatOpenAI(temperature=1, model="gpt-3.5-turbo", openai_api_key=OPEN_API_KEY)
        self.industries = list(IndustryType.objects.all().values_list("industry_type"))
        self.business_models = list(BusinessModelType.objects.all().values_list("business_model_type"))
        self.user_model = get_user_model()
        self.messages = []
        
    def run(self, user_id, **kwargs):

        with transaction.atomic():
            human_template = """
                They have skills in: {skills}
                They have a budget of: {budget}
            """
            human_prompt = HumanMessagePromptTemplate.from_template(human_template)

            response_schemas = [
                ResponseSchema(name="business_name", description="This is the name of the business you have generated"),
                ResponseSchema(name="business_idea", description="This is the business idea you will generate"),
                ResponseSchema(name="features", description="This is the array of product features you will generate"),
                ResponseSchema(name="execution_steps", description="This is the array of three execution steps you will generate"),
                ResponseSchema(name="follow_up_question", description="This is the follow up question you will generate"),
                ResponseSchema(name="business_model", description="This is the business model type for the business you will generate"),
                ResponseSchema(name="industry_type", description="This is the industry type the business is in will generate"),
            ]
            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

            chat_prompt = ChatPromptTemplate(
                messages=[self.system_prompt, human_prompt],
                input_variables=["business_models", "skills", "budget"],
                partial_variables={"format_instructions": output_parser.get_format_instructions()}
            )
            buisiness_query = chat_prompt.format_prompt(
                business_models=",".join(self.business_models),
                industry_types = ", ".join(self.industries),
                skills="sales, marketing", 
                budget="1000"
                )
            self.messages.extend(buisiness_query.to_messages())
            business_output = self.chat_model(self.messages)
            print(business_output)
            print()
            output = output_parser.parse(business_output.content)
            pprint.pprint(output)
            self.messages.append(business_output)
            self.messages.append(HumanMessage(content="What was the first and last feature you generated?"))
            ai_response = self.chat_model(self.messages)
            print(ai_response)
            self.messages.append(ai_response)
            self.messages.append(HumanMessage(content=output["follow_up_question"]))
            ai_response = self.chat_model(self.messages)
            print(ai_response)
            self.messages.append(ai_response)
            self.messages.append(HumanMessage(content="Summarize this entire conversation"))
            ai_response = self.chat_model(self.messages)
            self.messages.append(ai_response)
            print(ai_response)
            # twitter name available
            # webdomains available

            b_idea = BusinessIdea.objects.create(
                business_name=business_output["business_name"],
                business_idea=business_output["business_idea"],
                user=self.user_model.objects.get(id=user_id)
            )
            features_to_create = [
                Feature.objects.create(
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
            ExecutionStep.objects.create(execution_steps_to_create)

        return BusinessIdeaSerializer(b_idea).data
        



    