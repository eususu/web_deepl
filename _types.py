from typing import List, Optional
from pydantic import BaseModel

class TranslationRequest(BaseModel):
    text:str
    target_lang:str
    show_billed_characters:Optional[bool]=False


class Translations(BaseModel):
    detected_source_language: str
    text: str
    billed_characters: int

class TranslationResponse(BaseModel):
    translations:List[Translations]
    