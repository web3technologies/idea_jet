from decouple import config
from django.contrib.auth import get_user_model
from langchain.chat_models import ChatOpenAI
import openai


OPEN_API_KEY = config("OPEN_API_KEY")


class BaseGeneration:

    def __init__(self, model="gpt-3.5-turbo") -> None:
        openai.api_key = OPEN_API_KEY
        self.chat_model = ChatOpenAI(temperature=1, model=model, openai_api_key=OPEN_API_KEY)
        self.user_model = get_user_model()
        self.messages = []