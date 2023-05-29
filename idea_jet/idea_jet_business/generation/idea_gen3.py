from django.db import transaction
from decouple import config
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.schema import OutputParserException
from langchain.schema import HumanMessage
from langchain.prompts.chat import (
    HumanMessagePromptTemplate, 
    ChatPromptTemplate, 
    SystemMessagePromptTemplate
)
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool

from idea_jet_business.models import BusinessIdea, ConversationSummary, ExecutionStep, Feature
from idea_jet_catalog.models import BusinessModelType, IndustryType
from idea_jet_business.serializers import BusinessIdeaSerializer
from idea_jet_business.generation.base import BaseGeneration
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore

import faiss

from langchain.experimental import AutoGPT


class BusinessIdeaGenerationV3(BaseGeneration):

    def run(self, user_id, action, data):

        search = SerpAPIWrapper(serpapi_api_key=config("SERP_API_KEY"))
        tools = [
            Tool(
                name = "search",
                func=search.run,
                description="useful for when you need to answer questions about current events. You should ask targeted questions"
            ),
            WriteFileTool(),
            ReadFileTool(),
        ]
        # Define your embedding model
        
        # Initialize the vectorstore as empty
        

        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)
        vectorstore = FAISS(self.embeddings_model.embed_query, index, InMemoryDocstore({}), {})
        agent = AutoGPT.from_llm_and_tools(
            ai_name="Tom",
            ai_role="Assistant",
            tools=tools,
            llm=self.chat_model,
            memory=vectorstore.as_retriever(),
        )
        # Set verbose to be true
        agent.chain.verbose = True
        agent.run(["Give me 5 home business ideas."])