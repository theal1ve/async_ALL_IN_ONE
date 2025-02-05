from g4f.client import AsyncClient
import g4f



async def create_response(message) -> str:
    client = AsyncClient(provider=g4f.Provider.Yqcloud)

    response = await client.chat.completions.create(
        model=g4f.models.default,
        messages=[
            {"role": "user", "content": message}])
    
    res: str = (response.choices[0].message.content)
    
    return  res

