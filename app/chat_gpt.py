from g4f.client import AsyncClient
from pprint import pprint
import g4f



async def create_response(history: dict) -> str:
    if len(history) >= 9:
        del history[:2]
    print(len(history))
    pprint(history)
    client = AsyncClient(provider=g4f.Provider.Yqcloud)
    response = await client.chat.completions.create(
        model=g4f.models.default,
        messages=history)
    
    res: str = (response.choices[0].message.content)
    history.append({"role": "assistant", "content": res})
    return res, history


async def generate_image(message):
    client = AsyncClient(provider=g4f.Provider.Gemini)
    response = await client.images.generate(
        model="dall-e-3",
        prompt=f"ПОЖАЛУЙСТА, ВОСПРИНИМАЙ ЗАПРОС ПЕРЕВОДЯ ЕГО НА РУССКИЙ! Сгенерируй мне {message}",
        response_format="url",
        size="1024x1024"
    )
    
    
    return response.data[0].url

