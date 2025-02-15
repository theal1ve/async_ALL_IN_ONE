from datetime import datetime
from pydantic import BaseModel


class Users(BaseModel):
    id: int
    admin: int
    alive: int
    unlimit: int
    count_generate: int
    datetime_of_first_generate: datetime
    model_for_chat: str
    model_for_image: str
    promt_for_chat: str
