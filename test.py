import g4f.Provider
from g4f.client import AsyncClient
from pprint import pprint
import g4f
from aiogoogletrans import Translator
import asyncio

async def translate(text: str) -> str:
    translator = Translator()
    result = await translator.translate(text, src="ru", dest="en")
    return result.text



async def create_response(message):
    client = AsyncClient(provider=g4f.Provider.Blackbox)
    response = await client.chat.completions.create(
        model="deepseek-v3",
        messages=[{"role": "user", "content": ""}, {"role": "user", "content": message}])
    
    return response.choices



async def generate_image(text: str):
    translated_text = await translate(text)
    client = AsyncClient(provider=g4f.Provider.PollinationsImage)
    response = await client.images.generate(
        model='flux',
        prompt=translated_text,
        response_format="url",
        size="1024x1024"
    )
    
    
    return response.data[0].url


# print(asyncio.run(generate_image("розовый слоник")))
pprint(asyncio.run(create_response("как дела?")))
