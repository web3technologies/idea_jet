from decouple import config

from langchain import PromptTemplate
from langchain.chains import APIChain, ConversationChain, LLMChain, RetrievalQA, SimpleSequentialChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import openai
import pprint
import random

import industry_list


template_2 = """
        I am this type of founder {founder_type}
        - Who else do I need to hire to make this busines work?
    """

OPEN_API_KEY = config("OPEN_API_KEY")
openai.api_key = OPEN_API_KEY
llm = OpenAI(
            temperature=1, 
            openai_api_key=OPEN_API_KEY,
            
        )

# - Ask a question about the unique business idea

def main():
    
    buffer_memory = ConversationBufferMemory()

    idea_template = """
        You are a very successful entrepreneur. 
        Examples: {entrepreneurs} 
        You think like them.
        You have created many multi million dollar revenue businesses in the past.
        You have also raised millions of dollars in funding and have exited with multi million dollar exits.

        Your goal is to:
        - Generate a unique business idea in this industry: {industry}
        - Generate a name for this business

        YOUR RESPONSE:

    """
    idea_prompt = PromptTemplate(
        input_variables=["entrepreneurs", "industry"], 
        template=idea_template
    )
    random_industry = random.choice(industry_list.industry_list)
    print(f"INDUSTRY: {random_industry}")

    business_idea_chain = LLMChain(llm=llm, prompt=idea_prompt)
    business_idea = business_idea_chain.predict(
            entrepreneurs=", ".join(["Peter thiel", ", Elon Musk", "Jeff Bezos"]),
            industry=random_industry
    )
    print(business_idea)
    print()
    # ask_questions(business_idea, buffer_memory)
    # ask_questions_conv(buffer=buffer_memory, idea=business_idea)
    business_idea_data = get_final_idea(buffer_memory=buffer_memory, business_idea=business_idea)
    logo_url = get_logo(business_idea_data.get("business_name"))
    business_idea_data["logo"] = logo_url
    return business_idea_data

def get_logo(business_name):
    print("Creating logo...")
    response = openai.Image.create(
        prompt=f"Create a simple animated logo for the business name {business_name}",
        n=1,
        size="256x256"
    )
    image_url = response['data'][0]['url']
    return image_url
  


def get_final_idea(buffer_memory, business_idea):
    print("Generating final business idea...")
    final_output_template = """
        After re reading the business idea and looking through the memory of this idea generation I want you to create a business:

        {bus_idea}

        - Return the business name
        - Return the business idea
        - Generate a pricing model
        - Generate a finance model
        - Generate a marketing strategy
        - Create a simple white paper in less than 200 characters
        
        {format_instructions}

        YOUR RESPONSE:
    """

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

    final_idea_chain = LLMChain(llm=llm, prompt=final_idea_prompt, memory=buffer_memory)
    final_idea_res = final_idea_chain.run(business_idea)
    final_idea_idea_dict = output_parser.parse(final_idea_res)

    return final_idea_idea_dict

def ask_questions_conv(buffer, idea):

    question_template = """
        Ask a unique question about the business idea: \n
        
        Idea: {idea}

        that can be used to improve your own understanding and the effectiveness of the business.
        Look in the conversation history and ensure you have not already asked this question.

        I want you to ask questions that can help any of these subjects:
            - Help improve customer retention
            - Generate the best marketing strategy
            - Deploy a successful marketing strategy
            - Secure financing from Ventur Capital firms
        
        After asking the question I want you to answer it with the best of your abilities. 
        Remember you are a very successful entrepreneur. You have created many successful businesses in the past.

        YOUR RESPONSE:

    """

    question_prompt = PromptTemplate(input_variables=["idea"], template=question_template)

    for n in range(1,6):
        question_chain = LLMChain(llm=llm, memory=buffer, prompt=question_prompt)
        output = question_chain.predict(idea=idea)
        print(output)
        print()


if __name__ == "__main__":
    idea = main()
    pprint.pprint(idea)