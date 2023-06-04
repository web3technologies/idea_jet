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
            - Pick a business idea that is not over saturated
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

    tot_template = """
        For the business idea you have generated I want you to evaluate its potential 
        Consider their pros and cons, initial effort needed, implementation difficulty, potential challenges, and the expected outcomes. 
        Assign a probability of success and a confidence level to each option based on these factors.
    """

    tot_template_2 = """
        For the business idea, deepen the thought process. 
        Generate product, potential scenarios, strategies for implementation, any necessary partnerships or resources, and how potential obstacles might be overcome. 
        Also, consider any potential unexpected outcomes and how they might be handled.
    """


    def _generate_random_idea(self, *args):

        chat_prompt = ChatPromptTemplate(
            messages=[self.system_prompt, self.few_shot_prompt, self.human_prompt],
            input_variables=["industry"]
        )
        industry = random.choice(self.industries_l)
        print(industry)
        business_query = chat_prompt.format_prompt(industry=industry).to_messages()

        initial_idea = self.chat_model(business_query)
        self.messages.append(initial_idea)

        self.messages.append(HumanMessage(content=self.tot_template_2))
        res_2 = self.chat_model(self.messages)
        self.messages.append(res_2)

        self.messages.append(HumanMessage(content=self.tot_template_3))
        res_3 = self.chat_model(self.messages)
        self.messages.append(res_3)

        final_idea_template = """
            Lets think through this step by step:
            
            Based on the idea with the most promise your job is to expand this idea to the best of your ability.
            Then you should perform the following actions:
            
            1 - Return the business name you have selected
            2 - Generate the expanded business idea
            3 - Then create a list of features for this business idea
            4 - Then create a list of execution steps for this business idea

            {format_instructions}
        """
        final_idea_prompt = HumanMessagePromptTemplate.from_template(final_idea_template)
        final_idea_chat = ChatPromptTemplate(
            messages=[final_idea_prompt],
            input_variables=[],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        self.messages.extend(final_idea_chat.format_prompt().to_messages())
        print("generating final output")
        final_idea = self.chat_model(self.messages)
        self.messages.append(final_idea)
        return final_idea


    def run(self, user_id, generation_id, *args, **kwargs):

        b_generation = BusinessGeneration.objects.get(id=generation_id)

        with transaction.atomic():

            business_idea = self._generate_random_idea()
            try:
                business_output_dict = self.output_parser.parse(business_idea.content)
            except OutputParserException as e:
                print("json error attempting to fix\n")
                print(business_idea.content + "\n")
                # catch the exception for the json output and tell chat gpt to correct the json
                self.messages.append(
                    HumanMessage(
                        content="You outputed incorrect json as described in the format instructions. Fix your output to follow the instructions."
                    )
                )
                business_output_dict = self.chat_model(self.messages)
                business_output_dict = self.output_parser.parse(business_idea.content)

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

        return {"business_idea_id": b_idea.id}
        



    