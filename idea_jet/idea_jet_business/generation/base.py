from decouple import config
from django.contrib.auth import get_user_model
from langchain.chat_models import ChatOpenAI
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.callbacks import get_openai_callback


OPEN_API_KEY = config("OPEN_API_KEY")


class BaseGeneration:

    def __init__(self, model="gpt-3.5-turbo") -> None:
        openai.api_key = OPEN_API_KEY
        self.chat_model = ChatOpenAI(temperature=1, model=model, openai_api_key=OPEN_API_KEY)
        self.embeddings_model = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
        self.user_model = get_user_model()
        self.messages = []
    
    def _count_tokens_agent(self, agent, query):
        with get_openai_callback() as cb:
            result = agent(query)
            print(f'Spent a total of {cb.total_tokens} tokens')

        return result


    # chain = LLMChain(
    #     prompt=PromptTemplate.from_template('tell us a joke about {topic}'),
    #     llm=ChatOpenAI(temperature=1, openai_api_key=OPEN_API_KEY, model="gpt-3.5-turbo")
    # )


    