from decouple import config
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import openai
import random
import requests

from idea_jet_business.models import BusinessIdea

from idea_jet_business.prompt_templates.business import *

OPEN_API_KEY = config("OPEN_API_KEY")

### notes
### possibly accept a budget. How much do you want to invest? Put this in the input.
### allow user to select how creative

class BusinessIdeaGeneration:

    def __init__(self) -> None:
        openai.api_key = OPEN_API_KEY
        self.llm = OpenAI(
                    temperature=1, 
                    openai_api_key=OPEN_API_KEY,  
                )
        self.user_model = get_user_model()
        
    def run(self, user_id, idea=None, industry=None, business_model=None, **kwargs):

        with transaction.atomic():
            buffer_memory = ConversationBufferMemory()
            if idea:
                template = idea_template
                input_vars = ["idea"]
                prediction_kwargs = {"idea": idea}
            elif industry:
                if business_model:
                    template = industry_and_model_template
                    input_vars = ["industry", "business_model"]
                    prediction_kwargs = {"industry": industry, "business_model": business_model}
                else:
                    template = industry_template
                    input_vars = ["industry"]
                    prediction_kwargs = {"industry":industry}
            else:
                template = random_template
                prediction_kwargs = {}
                input_vars = []

            idea_prompt = PromptTemplate(
                input_variables=input_vars, 
                template=template
            )
            
            business_idea_chain = LLMChain(llm=self.llm, prompt=idea_prompt)
            business_idea = business_idea_chain.predict(**prediction_kwargs)

            # ask_questions(business_idea, buffer_memory)
            # ask_questions_conv(buffer=buffer_memory, idea=business_idea)
            business_idea_data = self._get_final_idea(buffer_memory=buffer_memory, business_idea=business_idea)
            logo_url = self._get_logo(business_idea_data.get("business_name"))
            business_idea_data["logo"] = logo_url
            logo = self._create_uploadable_image(
                logo_url, 
                business_name=business_idea_data["business_name"]
            )
            BusinessIdea.objects.create(
                business_name=business_idea_data["business_name"],
                business_idea=business_idea_data["business_idea"],
                pricing_model=business_idea_data["pricing_model"], 
                finance_model=business_idea_data["finance_model"], 
                marketing_strategy=business_idea_data["marketing_strategy"], 
                white_paper=business_idea_data["white_paper"], 
                logo=logo,
                user=self.user_model.objects.get(id=user_id)
            )
            return business_idea_data
        
    def _get_logo(self, business_name):
        response = openai.Image.create(
            prompt=f"Create a simple animated logo for the business name {business_name}",
            n=1,
            size="256x256"
        )
        image_url = response['data'][0]['url']
        return image_url
    
    def _create_uploadable_image(self, url, business_name):
        response = requests.get(url)
        image_content = ContentFile(response.content)
        image_path = default_storage.save(f"{business_name}.png", image_content)
        return image_path
  
    def _get_final_idea(self, buffer_memory, business_idea):
        print("Generating final business idea...")

        response_schemas = [
            ResponseSchema(name="business_name", description="This is the name of the business you have generated"),
            ResponseSchema(name="business_idea", description="This is the business idea you will generate"),
            ResponseSchema(name="pricing_model", description="This is the pricing model you will generate for the business idea"),
            ResponseSchema(name="finance_model", description="This is the finance model you will generate for the business idea"),
            ResponseSchema(name="marketing_strategy", description="This is the marketing strategy you will generate for the business idea"),
            ResponseSchema(name="white_paper", description="The simple white paper in less than 200 characters")
        ]

        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        final_idea_prompt = PromptTemplate(
            input_variables=["bus_idea"],
            partial_variables={"format_instructions": format_instructions},
            template=final_output_template
        )

        final_idea_chain = LLMChain(llm=self.llm, prompt=final_idea_prompt, memory=buffer_memory)
        final_idea_res = final_idea_chain.run(business_idea)
        final_idea_idea_dict = output_parser.parse(final_idea_res)

        return final_idea_idea_dict

    def ask_questions_conv(self, buffer, idea):

        question_prompt = PromptTemplate(input_variables=["idea"], template=question_template)

        for n in range(1,6):
            question_chain = LLMChain(llm=self.llm, memory=buffer, prompt=question_prompt)
            output = question_chain.predict(idea=idea)
            print(output)
            print()