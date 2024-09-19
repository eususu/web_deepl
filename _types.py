from typing import List
from pydantic import BaseModel


class TranslationRequest(BaseModel):
    auth_key:str
    text:str
    target_lang:str


class Translations(BaseModel):
    detected_source_language: str
    text: str
    billed_characters: int

class TranslationResponse(BaseModel):
    translations:List[Translations]
    