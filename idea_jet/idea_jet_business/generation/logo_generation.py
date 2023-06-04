from django.core.files.base import ContentFile
from langchain.schema import HumanMessage
import openai
import requests

from idea_jet_business.models import BusinessIdea, Logo
from idea_jet_business.generation.base import BaseGeneration


class LogoGenerator(BaseGeneration):

    def run(self, business_idea_id, n=None, *args, **kwargs):

        if not type(n) == int:
            raise ValueError("n must be a valid integer representing the image ")

        b_idea = BusinessIdea.objects.get(id=business_idea_id)
        
        self.messages.append(
            HumanMessage(
                content=f"Given this business idea delimmited by backticks ```{b_idea.business_idea}```describe a design for a logo. Give a simple list of instructions in 25 words."
            )
        )
        description = self.chat_model(self.messages).content
        logos = b_idea.logos.all()
        curr_logo_count = len(logos)
        filename=f"{b_idea.business_name}_{curr_logo_count+n}.png"
        if logos.filter(file=filename):
            raise ValueError(f"{filename} logo already exists.")

        response = openai.Image.create(
            prompt=f"Create a clear logo with this description: {description}",
            n=1,
            size="256x256"
        )
        image_url = response['data'][0]['url']

        content_res = requests.get(image_url)
        content_res.raise_for_status()

        image_content= ContentFile(content_res.content)
        logo = Logo(business_idea=b_idea)
        logo.file.save(filename, image_content, save=True)
        return filename