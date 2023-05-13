from decouple import config
import openai
import os
import requests


OPEN_API_KEY = config("OPEN_API_KEY")


class LogoGenerator:

    def __init__(self) -> None:
        openai.api_key = OPEN_API_KEY
        
    def run(self, n):
        logos = []
        for i in range(0,n):
            logo = self._get_logo("IdeaJet", i)
            logos.append(logo)
        return logos
    
    def improve_image(self, image_path):
        response = openai.Image.create_variation(
            image=open(image_path, "rb"),
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        new_name = f"{image_path.split('.png')[0]}_edit.png"
        output = self._write_image_to_disk(image_url, new_name)
        return output
        
    def _get_logo(self, business_name, i):
        print(f"Creating logo {i} ...")
        response = openai.Image.create(
            prompt=f'Animated Luxury Private Jet Logo',
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        output_file = f"{os.getcwd()}/{business_name}_{i}.png"
        self._write_image_to_disk(image_url, output_file)
        return output_file
    
    def _write_image_to_disk(self, image_url, output_file):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            with open(output_file, 'wb') as file:
                file.write(response.content)
            
            print(f"Successfully downloaded and saved the PNG file as {output_file}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        return output_file
    
    

if __name__ == "__main__":
    files = LogoGenerator().run(n=16)
    # files = os.listdir(f"{os.getcwd()}/images/")
    # generator = LogoGenerator()
    # for file in files:
    #     generator.improve_image(f"{os.getcwd()}/images/{file}")