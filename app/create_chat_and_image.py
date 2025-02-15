import g4f.Provider
from g4f.client import AsyncClient
import g4f
from aiogoogletrans import Translator

async def translate(text: str) -> str:
    translator = Translator()
    result = await translator.translate(text, src="ru", dest="en")
    return result.text


async def create_response(history: dict, model: str):
    if len(history) >= 9:
        del history[:2]
    if model == "gpt-4":
        provider = g4f.Provider.Yqcloud
    else:
        provider = g4f.Provider.Blackbox
    client = AsyncClient(provider=provider)
    response = await client.chat.completions.create(
        model=model,
        messages=history)
    
    res: str = (response.choices[0].message.content)
    history.append({"role": "assistant", "content": res})
    return res, history


async def generate_image(text: str, model: str):
    translated_text = await translate(text)
    client = AsyncClient(provider=g4f.Provider.PollinationsImage)
    response = await client.images.generate(
        model=model,
        prompt=translated_text,
        response_format="url",
        size="1024x1024"
    )
    
    
    return response.data[0].url

