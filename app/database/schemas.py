from datetime import datetime
from typing import Optional

from pydantic import BaseModel




class Users(BaseModel):
    id: int
    admin: int
    alive: int
    unlimit: int
    count_generate: int
    datetime_of_first_generate: datetime