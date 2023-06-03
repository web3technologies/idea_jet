from django.db import transaction
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import OutputParserException
from langchain.schema import HumanMessage
from langchain.prompts.chat import (
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
    SystemMessagePromptTemplate
)
import random

from idea_jet_business.models import BusinessIdea, BusinessGeneration, ConversationSummary, ExecutionStep, Feature
from idea_jet_catalog.models import BusinessModelType, IndustryType
from idea_jet_business.serializers import BusinessIdeaSerializer

from .base_business_idea import BaseBusinessIdea


class BusinessIdeaGenerationRandom(BaseBusinessIdea):


    def _generate_random_idea(self, *args):
        ### few shot prompting here. Get a list of all companies and add name and business idea to the Catalog and use those as the few shot prompt
        ### make sure to instruct the ai not to copy but find a competitive advantage
        ### scrape startup pages to populate the database every day
        human_template = """
            Your task is to perform the following actions:
            1 - Generate a unique startup business idea in the industry delimited by triple backticks. 
                - Focus the unique startup business idea on quick to build minimum viable products. 
                - Focus the unique startup business idea on low barier to entry ideas.
                - Ensure that the unique business idea has a competitive advantage that will set it apart from its competitors.  
                - The unique startup business idea should be detailed in 100 or more words.
                - Brainstorm about new opportunities.
                - Do you not generate any ideas relating to eco friendly businesses
            2 - Generate a name for this unique startup business idea
            3 - Generate an array of product Key Features and Benefits for this unique startup business idea

            Industry: ```{industry}```
        """
            # {format_instructions}
            # 4 - Generate an array of three execution steps for this unique startup business idea
            # 5 - Generate a score for how original the unique startup business idea is
            # 6 - Generate a score for business potential for the unique startup business idea
            # 7 - Generate a reason for why you chose this potential for the score unique startup business idea
            # 8 - Generate a startup difficulty score for the unique startup business idea
            # 9 - Generate a reason for why you chose this difficulty score for the unique startup business idea

        human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate(
            messages=[self.system_prompt, self.few_shot_prompt, human_prompt],
            input_variables=["industry"]
        )
        industry = random.choice(self.industries_l)
        print(industry)
        business_query = chat_prompt.format_prompt(industry=industry).to_messages()
        return business_query


    def run(self, user_id, action, data, generation_id):

        b_generation = BusinessGeneration.objects.get(id=generation_id)

        with transaction.atomic():

            business_query = self._generate_random_idea()
            self.messages.extend(business_query)

            idea_to_use = self._generate_idea_with_tree_of_thought(action)
            
            self.messages.append(idea_to_use)
            try:
                business_output_dict = self.output_parser.parse(idea_to_use.content)
            except OutputParserException as e:
                print("json error attempting to fix\n")
                print(idea_to_use.content + "\n")
                # catch the exception for the json output and tell chat gpt to correct the json
                self.messages.append(
                    HumanMessage(
                        content="You outputed incorrect json as described in the format instructions. Fix your output to follow the instructions."
                    )
                )
                business_output_dict = self.chat_model(self.messages)
                business_output_dict = self.output_parser.parse(idea_to_use.content)

            print("creating objects")
            b_idea = BusinessIdea.objects.create(
                business_name=business_output_dict["business_name"],
                business_idea=business_output_dict["business_idea"],
                original_user=self.user_model.objects.get(id=user_id),
                business_generation=b_generation
            )
            print(business_output_dict["product"])
            features_to_create = [
                Feature(
                    feature=feature,
                    business_idea=b_idea
                )
                for feature in business_output_dict.get("features")
            ]
            execution_steps_to_create = [
                ExecutionStep(
                    execution_step=execution_step,
                    business_idea=b_idea
                )
                for execution_step in business_output_dict.get("execution_steps")
            ]
            Feature.objects.bulk_create(features_to_create)
            ExecutionStep.objects.bulk_create(execution_steps_to_create)

        return {"generation_id": b_generation.id}
        



    