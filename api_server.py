import asyncio
from contextlib import asynccontextmanager
import logging
import queue
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import argparse

from _types import TranslationRequest, TranslationResponse
from job_queue import JobQueue

class AppContext(BaseModel):
    job_queue: JobQueue
    target_lang: str

    class Config:
        arbitrary_types_allowed = True  # 사용자 정의 타입 허용

DEFAULT_MAX_JOB=3
app_context:AppContext = None

logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO, 
    format='%(asctime)s:%(name)s:%(levelname)s:PID(%(process)d):TID(%(thread)d):%(funcName)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app:FastAPI):
    logging.info("starting up server...")
    parser = argparse.ArgumentParser(description="API 서버 실행")
    parser.add_argument('--max_thread_length', type=int, default=DEFAULT_MAX_JOB, help='최대 스레드 수')
    parser.add_argument('--target_lang', type=str, default='KO', help='대상 언어')
    args = parser.parse_args()

    global app_context
    app_context = AppContext(job_queue=JobQueue(num_workers=args.max_thread_length), target_lang=args.target_lang)
    app_context.job_queue.start()
    yield
    logging.info("shutting down server...")
    app_context.job_queue.stop()  # 서버 종료 시 스레드 안전하게 종료

    
app = FastAPI(lifespan=lifespan)

@app.post("/v2/translate")
async def v2_translate(request:TranslationRequest)->TranslationResponse:
    async def job(request:TranslationRequest):
        logging.info(f"running job with param: {request}")
        return request

    try:
        global app_context
        app_context.job_queue.check()

        logging.info("add job")
        response:TranslationResponse = await app_context.job_queue.add_job(lambda: job(request))  # 파라미터 전달
        return response
    except asyncio.TimeoutError:
        logging.error("timeout")
        return JSONResponse(
            status_code=503,
            content={"message": "서버가 불안정합니다. 나중에 다시 시도해주세요."}
        )
    except queue.Full:
        logging.error("queue is full")
        return JSONResponse(
            status_code=503,
            content={"message": f"{request} 큐가 가득 차 있습니다. 나중에 다시 시도해주세요."}
        )
@app.get("/")
async def root():
    await asyncio.sleep(1)  # 작업 시뮬레이션
    return {"message": "Hello World"}

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

