
from decouple import config
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
from langchain import HuggingFaceHub



class BusinessIdeaGenerationRandom2:

    def __init__(self) -> None:
        self.openai_api_key = config("OPENAI_API_KEY")
        self.hf_api_key = config("HUGGINGFACE_API_TOKEN")
        repo_id1 = "gpt2"
        repo_id2 = "facebook/opt-350m"

        llm_1 = OpenAI(temperature=1, openai_api_key=self.openai_api_key)
        llm_2 = HuggingFaceHub(repo_id=repo_id1, model_kwargs={"temperature":1}, huggingfacehub_api_token=self.hf_api_key)
        llm_3 = HuggingFaceHub(repo_id=repo_id2, model_kwargs={"temperature":1}, huggingfacehub_api_token=self.hf_api_key)

    def run(self):

        template_1 = """
            
        """

        prompt1 = PromptTemplate(template=template_1, input_variables=[])

        llm_chain_1 = LLMChain(prompt=prompt1, llm=self.llm_1)
        llm_chain_2 = LLMChain(prompt=prompt1, llm=self.llm_2)
        llm_chain_3 = LLMChain(prompt=prompt1, llm=self.llm_3)

        response_1 = llm_chain_1.run()
        response_2 = llm_chain_2.run()
        response_3 = llm_chain_3.run()

