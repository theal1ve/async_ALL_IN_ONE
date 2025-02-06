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


