from datetime import datetime
from typing import Optional

from pydantic import BaseModel




class Users(BaseModel):
    id: int
    admin: int
    alive: int
    unlimit_questions: int