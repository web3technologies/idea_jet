from django.db import transaction
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import OutputParserException
from langchain.schema import HumanMessage
from langchain.prompts.chat import (
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
    SystemMessagePromptTemplate
)

from idea_jet_business.models import BusinessIdea, ConversationSummary, ExecutionStep, Feature
from idea_jet_catalog.models import BusinessModelType, IndustryType
from idea_jet_business.serializers import BusinessIdeaSerializer
from idea_jet_business.generation.base import BaseGeneration


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
        Use these examples delimited by triple backticks to help you create a new and unique idea, that has the same level of business potential as these startups.

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
            5 - Generate a score for how original the business idea is
            6 - Generate a score for business potential
            7 - Generate a startup difficulty score
            8 - Generate a reason for why you chose this difficulty score
            {format_instructions}
    """

            # - Generate the business model type for the business based on these business models {business_models}
            # - Generate the industry type the business is in based on these {industry_types}    
    system_prompt = SystemMessagePromptTemplate.from_template(system_template)
    system_prompt_2 = SystemMessagePromptTemplate.from_template(system_template_2)
    few_shot_prompt = SystemMessagePromptTemplate.from_template(few_shot_template)

    def __init__(self, model="gpt-3.5-turbo") -> None:
        super().__init__(model)
        self.industries = list(IndustryType.objects.all().values_list("industry_type", flat=True))
        self.business_models = list(BusinessModelType.objects.all().values_list("business_model_type", flat=True))
        self.response_schemas = [
                ResponseSchema(name="business_name", description="This is the name of the business you have generated"),
                ResponseSchema(name="business_idea", description="This is the detailed business idea you will generate"),
                ResponseSchema(name="features", description="This is the array of product features you will generate"),
                ResponseSchema(name="execution_steps", description="This is the array of three execution steps you will generate"),
                ResponseSchema(name="originality_score", description="This is the originality score you will generate"),
                ResponseSchema(name="potential_score", description="This is the business potential score you will generate"),
                ResponseSchema(name="difficulty_score", description="This is the startup difficulty score you will generate"),
                ResponseSchema(name="difficulty_reason", description="This is the difficulty reason you will generate"),
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
        ### few shot prompting here. Get a list of all companies and add name and business idea to the Catalog and use those as the few shot prompt
        ### make sure to instruct the ai not to copy but find a competitive advantage
        ### scrape startup pages to populate the database every day
        human_template = """Generate a random and unique business idea in the industry delimited by triple backticks ```{industry}```"""
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate(
            messages=[self.system_prompt, self.few_shot_prompt, human_prompt, self.system_prompt_2],
            input_variables=["industry"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        business_query = chat_prompt.format_prompt(industry="FinTech").to_messages()
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
    

    # def _summarize():
        # print("summarizing conversation...")
        # self.messages.append(HumanMessage(content="Summarize this entire conversation"))
        # ai_conversation_summary = self.chat_model(self.messages)
        # self.messages.append(ai_conversation_summary)
                    # conversation_summary = ConversationSummary.objects.create(
        #     business_idea=b_idea,
        #     summary=ai_conversation_summary.content,
        #     type="INITIAL"
        # )
        
    def run(self, user_id, action, data):

        with transaction.atomic():

            business_query = self.idea_generation_mapping[action](data)
            self.messages.extend(business_query)

            print(f"generating {action} idea ... \n")
            business_output = self.chat_model(self.messages)
            self.messages.append(business_output)

            try:
                business_output_dict = self.output_parser.parse(business_output.content)
            except OutputParserException as e:
                print("json error attempting to fix\n")
                print(business_output.content + "\n")
                # catch the exception for the json output and tell chat gpt to correct the json
                self.messages.append(HumanMessage(content="You outputed incorrect json as described earlier. Fix this and output correct json."))
                business_output_dict = self.chat_model(self.messages)
                business_output_dict = self.output_parser.parse(business_output.content)

            print(f"originality: {business_output_dict['originality_score']}")
            print(f"potential: {business_output_dict['potential_score']}")
            print(f"difficulty: {business_output_dict['difficulty_score']}")
            print(f"difficulty reason: {business_output_dict['difficulty_reason']}")
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
        



    