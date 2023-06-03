from django.db import transaction
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import OutputParserException
from langchain.schema import HumanMessage
from langchain.prompts.chat import (
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
)

from idea_jet_business.models import BusinessIdea, MarketResearch
from .base import BaseGeneration


### NEED TASKS FOR
## Launch Strategey
## Competitor Analysis

class MarketResearchGenerator(BaseGeneration):

    def run(self, business_id):

        with transaction.atomic():
            print("Generating Market research")

            business_idea = BusinessIdea.objects.get(id=business_id)

            market_research_template = """
            I want you to perform in depth market research on the business idea generated:
            {business_idea}

            Target Market and Customers:
            Define the specific target market segment or segments that you are researching.
            Understand the demographics, psychographics, and behaviors of your target customers.
            Identify their needs, preferences, pain points, and purchasing behaviors.
            
            Market Size and Growth Potential:
            Determine the size of the market or industry you are analyzing.
            Assess the historical growth rate and projected future growth of the market.
            Identify any emerging trends, technologies, or regulatory changes that may impact the market.
            Stay informed about industry trends, innovations, and technological advancements.
            Consider economic, social, political, and environmental factors that may impact the market.
            Analyze regulatory frameworks, standards, and certifications relevant to the industry.
            
            Pricing and Revenue Potential:
            Assess the pricing strategies and models used by competitors in the market.
            Understand customers' price sensitivity, perceived value, and willingness to pay.
            Estimate the revenue potential and profitability of your product or service based on market dynamics and pricing considerations.
            
            Barriers to Entry:
            Identify the barriers to entry in the market, such as regulatory requirements, capital investments, or intellectual property protection.
            Understand the challenges and risks associated with entering the market.
            Assess the competitive landscape and potential strategies to overcome barriers to entry.
            
            Market Positioning and Differentiation:
            Determine how your product or service will differentiate itself from competitors in the market.
            Understand the unique value proposition and key messaging that will resonate with your target customers.
            Assess potential positioning strategies and identify areas of competitive advantage.

            {format_instructions}
        """
        human_prompt = HumanMessagePromptTemplate.from_template(market_research_template)

        response_schemas = [
                ResponseSchema(name="target_market", description="This is target markets and customers you will define"),
                ResponseSchema(name="market_size", description="This is the market size and growth you will define"),
                ResponseSchema(name="pricing_model", description="This is the pricing and revenue model you will define"),
                ResponseSchema(name="barriers", description="This is the barriers to entry you will define"),
                ResponseSchema(name="market_positioning", description="This is the market_positioning you will define"),
            ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

        chat_prompt = ChatPromptTemplate(
            messages=[human_prompt],
            input_variables=["business_idea"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()}
        )
        market_research_query = chat_prompt.format_prompt(business_idea=business_idea.business_idea).to_messages()
        self.messages.extend(market_research_query)
        market_resarch_generated = self.chat_model(self.messages)
        self.messages.append(market_resarch_generated)

        try:
            market_resarch_generated_dict = output_parser.parse(market_resarch_generated.content)
        except OutputParserException as e:
            print("json error in market research attempting to fix")
            # catch the exception for the json output and tell chat gpt to correct the json
            self.messages.append(HumanMessage(content="You outputed incorrect json as described earlier. Fix this and output correct json."))
            market_resarch_generated_dict = self.chat_model(self.messages)
            market_resarch_generated_dict = output_parser.parse(market_resarch_generated.content)

        MarketResearch.objects.create(
            business_idea=business_idea,
            target_market=market_resarch_generated_dict["target_market"],
            market_size=market_resarch_generated_dict["market_size"],
            pricing_model=market_resarch_generated_dict["pricing_model"],
            barriers=market_resarch_generated_dict["barriers"],
            market_positioning=market_resarch_generated_dict["market_positioning"]
        )

        return market_resarch_generated_dict
            
        



    