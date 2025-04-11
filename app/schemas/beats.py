from pydantic import BaseModel
from typing import Optional


class BeatsBase(BaseModel):
    name: str
    image_path: str
    audio_path: str
    exclusive: Optional[bool] = False


class BeatsCreate(BeatsBase):
    pass


class BeatsRead(BeatsBase):
    id: int

    class Config:
        orm_mode = True
