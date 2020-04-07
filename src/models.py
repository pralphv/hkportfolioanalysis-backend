from typing import Dict

from pydantic import BaseModel


class Bundle(BaseModel):
    stockObj: Dict
    buyDate: str
