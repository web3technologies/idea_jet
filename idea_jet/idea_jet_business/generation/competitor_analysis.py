from django.db import transaction
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import OutputParserException
from langchain.schema import HumanMessage
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate, 
    ChatPromptTemplate, 
)

from idea_jet_business.models import BusinessIdea, Competitor
from .base import BaseGeneration



class CompetitorAnalysisGenerator(BaseGeneration):


    system_template = """"
        You work on a team to provide competitor analysis for companies.
        You are an expert at finding the competitions strength and weaknesses.
    """

    market_research_template = """
            I want you to perform in depth competitor analysis on the business idea generated:
            {business_idea}

            Your job is to provide a list of competitors with an Overview, Key Features, and competitors Competitive Advantage.
            Do not summarize the data.

            {format_instructions}
        """

    def run(self, business_id):

        with transaction.atomic():
            print("Generating Competitive Analysis")

            business_idea = BusinessIdea.objects.get(id=business_id)

            system_prompt = SystemMessagePromptTemplate.from_template(self.system_template)
            human_prompt = HumanMessagePromptTemplate.from_template(self.market_research_template)

            response_schemas = [
                    ResponseSchema(
                        name="competitors", 
                        description="array of competitor objects containing name, overview, array of key features and competitors Competitive Advantage."
                )
            ]
            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

            chat_prompt = ChatPromptTemplate(
                messages=[system_prompt, human_prompt],
                input_variables=["business_idea"],
                partial_variables={"format_instructions": output_parser.get_format_instructions()}
            )
            market_research_query = chat_prompt.format_prompt(business_idea=business_idea.business_idea).to_messages()
            self.messages.extend(market_research_query)
            competetive_analysis_generated = self.chat_model(self.messages)
            self.messages.append(competetive_analysis_generated)
            
            # self.messages.append(
            #     HumanMessage(content=f"Based on these competitors output some competitive advantages I can implement for {business_idea.business_idea}")
            #     )
            
            # print(self.chat_model(self.messages))

            try:
                competetive_analysis_generated_dict = output_parser.parse(competetive_analysis_generated.content)
            except OutputParserException as e:
                print("json error in competitor analysis to fix")
                # catch the exception for the json output and tell chat gpt to correct the json
                self.messages.append(HumanMessage(content="You outputed incorrect json as described earlier. Fix this and output correct json."))
                competetive_analysis_generated_dict = self.chat_model(self.messages)
                competetive_analysis_generated_dict = output_parser.parse(competetive_analysis_generated.content)

            competitors = [
                Competitor(
                    business_idea=business_idea,
                    name=competitor["name"],
                    overview=competitor["overview"],
                    key_features=competitor.get("key_features", competitor.get("keyFeatures")),
                    competitive_advantage=competitor["competitive_advantage"],
                )
                for competitor in competetive_analysis_generated_dict["competitors"]
            ]
            Competitor.objects.bulk_create(competitors)

        return competetive_analysis_generated_dict
            
        



    