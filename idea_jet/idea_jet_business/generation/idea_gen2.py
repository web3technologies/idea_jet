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

from idea_jet_business.models import BusinessIdea, ConversationSummary, ExecutionStep, Feature
from idea_jet_catalog.models import BusinessModelType, IndustryType
from idea_jet_business.serializers import BusinessIdeaSerializer
from idea_jet_business.generation.base import BaseGeneration
import openai



class BusinessIdeaGenerationV2(BaseGeneration):

    system_template = """
            You are a very successful entrepreneur. 
            Examples: "Peter thiel", "Elon Musk", "Jeff Bezos"
            You think like them.
            You have created many multi million dollar revenue businesses in the past.
            You have also raised millions of dollars in funding and have exited with multi million dollar exits.
        """
    
    few_shot_template = """
        Here are some examples of startups in the past that have been successful:
        Examples are delimited by triple backticks.

        Examples:
        ``` 1. Robinhood
                Business Idea: A Financial services platform that offers commission-free trading for stocks, ETFs, options, and cryptocurrencies. Aimed at making financial markets more accessible to the average person.
                Industry: FinTech
                Features:
                    Commission-free trading
                    Accessibility to various types of investments (stocks, ETFs, options, cryptocurrencies)
                    User-friendly interface
            2. Nubank
                Business Idea: Brazilian neobank and the largest Fintech in Latin America. It provides services like fee-free credit cards, personal loans, free transfer accounts, and investment options.
                Industry: FinTech
                Features:
                    Fee-free credit cards
                    Personal loans
                    Free transfer accounts
            3. Klarna
                Business Idea: Swedish fintech company that provides online financial services such as payments for online storefronts and direct payments, post-purchase payments, and more.
                Industry: FinTech
                Features:
                    Online payment services
                    Direct payments
                    Post-purchase payments
            4. Canva
                Business Idea: Online design and publishing tool with a simple drag-and-drop interface. It provides free access to a wide variety of design tools and options, as well as premium options for paying customers.
                Industry: Design
                Features:
                    Drag-and-drop design interface
                    Variety of design tools and options
                    Free access with premium options
            5. Coursera
                Business Idea: American online learning platform that offers massive open online courses (MOOC), specializations, and degrees in a variety of subjects from universities and institutions around the world.
                Industry: EdTech
                Features:
                    Offers Massive Open Online Courses (MOOCs)
                    Provides specializations and degrees
                    Collaborates with universities and institutions around the world```
    """

    system_template_2 = """
        Your task is to perform the following actions:
            1 - Generate a unique, original and detailed business idea
            2 - Generate a name for this business
            3 - Generate an array of product Key Features and Benefits
            4 - Generate an array of three execution steps
            {format_instructions}
    """

    tot_template = """
        For each of the three proposed business ideas delimited by tripple backticks, evaluate their potential. 
        Consider their pros and cons, initial effort needed, implementation difficulty, potential challenges, and the expected outcomes. 
        Assign a probability of success and a confidence level to each option based on these factors.
        ```{ideas}```
    """

    tot_template_2 = """
        For each business idea, deepen the thought process. 
        Generate potential scenarios, strategies for implementation, any necessary partnerships or resources, and how potential obstacles might be overcome. 
        Also, consider any potential unexpected outcomes and how they might be handled.
    """

    tot_template_3 = """
        Based on the evaluations and scenarios, rank the business ideas in order of promise. 
        Provide a justification for each ranking and offer any final thoughts or considerations for each business idea
    """

            # - Generate the business model type for the business based on these business models {business_models}
            # - Generate the industry type the business is in based on these {industry_types}    
    system_prompt = SystemMessagePromptTemplate.from_template(system_template)
    system_prompt_2 = SystemMessagePromptTemplate.from_template(system_template_2)
    few_shot_prompt = SystemMessagePromptTemplate.from_template(few_shot_template)

    tot_prompt = HumanMessagePromptTemplate.from_template(tot_template)
    tot_prompt_2 = HumanMessagePromptTemplate.from_template(tot_template_2)
    tot_prompt_3 = HumanMessagePromptTemplate.from_template(tot_template_3)


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
        self.industries = list(IndustryType.objects.all().values_list("industry_type", flat=True))
        self.business_models = list(BusinessModelType.objects.all().values_list("business_model_type", flat=True))
        self.response_schemas = [
                ResponseSchema(name="business_name", description="This is the name of the business you have generated"),
                ResponseSchema(name="business_idea", description="This is the unique startup business idea you will generate"),
                ResponseSchema(name="features", description="This is the array of product features you will generate"),
                ResponseSchema(name="execution_steps", description="This is the array of three execution steps you will generate"),
                ResponseSchema(name="business_model", description="This is the business model type for the business you will generate"),
                ResponseSchema(name="industry_type", description="This is the industry type the business is in will generate"),
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
            input_variables=["industry"],
            # partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        industry = random.choice(self.industries_l)
        print(industry)
        business_query = chat_prompt.format_prompt(industry=industry).to_messages()
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
        human_template = """I have the start of a business idea and I want you to help me expand on this. Use the idea delimited by tripple back ticks to create a unique business. ```{existingIdea}```"""
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate(
            messages=[self.system_prompt, human_prompt, self.system_prompt_2],
            input_variables=["existingIdea"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        business_query = chat_prompt.format_prompt(existingIdea=data.get("existingIdea"))
        return business_query.to_messages()
    

    def _ask_questions(self, business_idea):

        questions = []
        for i in range(0,4):
            question = self.chat_model([HumanMessage(content=f"Ask a question about this bsuiness idea delimited by tripple backticks that can help you understand the idea better. ```{business_idea}```")])
            print(question.content)


    def _generate_idea_with_tree_of_thought(self, action):
        tot_messages = []
        bus_ideas = []
        for i in range(1,4):
            print(f"generating {action} idea #{i}... \n")
            business_output = self.chat_model(self.messages)
            bus_ideas.append(business_output.content)

        chat_prompt = ChatPromptTemplate(
            messages=[self.tot_prompt],
            input_variables=["ideas"],
        )
        query = chat_prompt.format_prompt(ideas="\n".join(bus_ideas))

        tot_messages.extend(query.to_messages())

        res = self.chat_model(tot_messages)
        print(res.content)
        tot_messages.append(res)
        
        tot_messages.append(HumanMessage(content=self.tot_template_2))
        res_2 = self.chat_model(tot_messages)
        print(res_2.content)
        tot_messages.append(res_2)

        tot_messages.append(HumanMessage(content=self.tot_template_3))
        res_3 = self.chat_model(tot_messages)
        print(res_3.content)

        return res_3


    def run(self, user_id, action, data):

        with transaction.atomic():

            business_query = self.idea_generation_mapping[action](data)
            self.messages.extend(business_query)

            idea_to_use = self._generate_idea_with_tree_of_thought(action)
            
            self.messages.append(idea_to_use)
            try:
                business_output_dict = self.output_parser.parse(idea_to_use.content)
            except OutputParserException as e:
                print("json error attempting to fix\n")
                print(idea_to_use.content + "\n")
                # catch the exception for the json output and tell chat gpt to correct the json
                self.messages.append(HumanMessage(content="You outputed incorrect json as described earlier. Fix this and output correct json."))
                business_output_dict = self.chat_model(self.messages)
                business_output_dict = self.output_parser.parse(idea_to_use.content)


            print("creating objects")
            try:
                b_idea = BusinessIdea.objects.create(
                    business_name=business_output_dict["business_name"],
                    business_idea=business_output_dict["business_idea"],
                    # business_model=BusinessModelType.objects.get(business_model_type=business_output_dict["business_model"]),
                    # industry_type=IndustryType.objects.get(industry_type=business_output_dict["industry_type"]),
                    original_user=self.user_model.objects.get(id=user_id)
                )
            except (BusinessModelType.DoesNotExist, IndustryType.DoesNotExist) as e:
                print(business_output_dict["business_model"])
                print(business_output_dict["industry_type"])
                raise e
            
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

        return BusinessIdeaSerializer(b_idea).data
        



    