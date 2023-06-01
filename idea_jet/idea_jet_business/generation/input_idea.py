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
from .base_business_idea import BaseBusinessIdea


class BusinessIdeaGenerationInput(BaseBusinessIdea):

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


    def run(self, user_id, action, data):

        with transaction.atomic():

            business_query = self._generate_input_idea(data)
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
        



    