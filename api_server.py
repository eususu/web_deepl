from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import requests
import os

app = FastAPI()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

class Translation(BaseModel):
    detected_source_language: str
    text: str

class TranslationResponse(BaseModel):
    translations: List[Translation]

@app.post("/v2/translate", response_model=TranslationResponse)
async def translate(
    text: List[str] = Query(..., description="텍스트 목록"),
    target_lang: str = Query(..., description="대상 언어"),
    source_lang: Optional[str] = Query(None, description="원본 언어 (선택사항)"),
    split_sentences: Optional[str] = Query("1", description="문장 분할 옵션"),
    preserve_formatting: Optional[bool] = Query(False, description="형식 유지"),
    formality: Optional[str] = Query(None, description="형식성 (선택사항)")
):
    headers = {
        "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"
    }
    
    payload = {
        "text": text,
        "target_lang": target_lang,
        "source_lang": source_lang,
        "split_sentences": split_sentences,
        "preserve_formatting": preserve_formatting,
        "formality": formality
    }
    
    try:
        response = requests.post(DEEPL_API_URL, headers=headers, data=payload)
        response.raise_for_status()
        result = response.json()
        return JSONResponse(content=result)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DeepL API 오류: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)