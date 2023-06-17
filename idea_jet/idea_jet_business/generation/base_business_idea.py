from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import HumanMessage
from langchain.prompts.chat import (
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
    SystemMessagePromptTemplate
)
from idea_jet_business.generation.base import BaseGeneration


class BaseBusinessIdea(BaseGeneration):

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

    tot_template = """
        For each of the three proposed business ideas delimited by tripple backticks, evaluate their potential. 
        Consider their pros and cons, initial effort needed, implementation difficulty, potential challenges, and the expected outcomes. 
        Assign a probability of success and a confidence level to each option based on these factors.
        ```{ideas}```
    """

    tot_template_2 = """
        For each business idea, deepen the thought process. 
        Generate product, potential scenarios, strategies for implementation, any necessary partnerships or resources, and how potential obstacles might be overcome. 
        Also, consider any potential unexpected outcomes and how they might be handled.
    """

    tot_template_3 = """
        Based on the evaluations and scenarios, rank the business ideas in order of promise. 
        Provide a justification for each ranking and offer any final thoughts or considerations for each business idea
    """

    tot_template_4 = """
        Pick the most promising business idea that you have selected and return all relevant data, scenar
    """

            # - Generate the business model type for the business based on these business models {business_models}
            # - Generate the industry type the business is in based on these {industry_types}    
    system_prompt = SystemMessagePromptTemplate.from_template(system_template)
    
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
        self.response_schemas = [
                ResponseSchema(name="business_name", description="This is the name of the business you have generated"),
                ResponseSchema(name="business_idea", description="This is the unique startup business idea you will generate"),
                ResponseSchema(name="product", description="This is the product you will generate"),
                ResponseSchema(name="features", description="This is the array of product features you will generate"),
            ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)


    def _generate_idea_with_tree_of_thought(self):
        tot_messages = []
        bus_ideas = []
        for i in range(1,4):
            print(f"generating random idea #{i}... \n")
            business_output = self.chat_model(self.messages)
            bus_ideas.append(business_output.content)

        chat_prompt = ChatPromptTemplate(
            messages=[self.tot_prompt],
            input_variables=["ideas"],
        )
        query = chat_prompt.format_prompt(ideas="\n".join(bus_ideas))

        tot_messages.extend(query.to_messages())

        print("performing analysis")
        res = self.chat_model(tot_messages)
        tot_messages.append(res)
        
        tot_messages.append(HumanMessage(content=self.tot_template_2))
        res_2 = self.chat_model(tot_messages)
        tot_messages.append(res_2)

        tot_messages.append(HumanMessage(content=self.tot_template_3))
        res_3 = self.chat_model(tot_messages)
        tot_messages.append(res_3)

        final_idea_template = """
            Lets think through this step by step:
            
            Based on the idea with the most promise your job is to expand this idea to the best of your ability.
            Then you should perform the following actions:
            
            1 - Generate the expanded business idea
            2 - Return the business name you have selected
            3 - Generate a detailed product design
            4 - Then create a list of features for this business idea

            {format_instructions}
        """
        final_idea_prompt = HumanMessagePromptTemplate.from_template(final_idea_template)
        final_idea_chat = ChatPromptTemplate(
            messages=[final_idea_prompt],
            input_variables=[],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
        tot_messages.extend(final_idea_chat.format_prompt().to_messages())
        print("generating final output")
        final_idea = self.chat_model(tot_messages)
        return final_idea

    