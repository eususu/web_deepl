import asyncio
import logging
import queue
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import sys

from deepl_bot import DeepLBot
from job_queue import JobQueue

app = FastAPI()
MAX_JOB=2

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s - %(process)d'
)

app = FastAPI()


job_queue = JobQueue(num_workers=MAX_JOB)

@app.on_event("startup")
def startup_event():
    job_queue.start()

@app.middleware("http")
async def queue_middleware(request, call_next):
    async def job(param):  # 파라미터 추가
        logging.info(f"running job with param: {param}")
        return param
        #return JSONResponse(content={"message": f"Job completed {param} successfully"})

    param = request.query_params.get("param", "default")  # 쿼리 파라미터에서 값 가져오기

    try:
        job_queue.check()
        response = await job_queue.add_job(lambda: job(param))  # 파라미터 전달
        return response
    except asyncio.TimeoutError:
        logging.error("timeout")
        return JSONResponse(
            status_code=503,
            content={"message": "서버가繁합니다. 나중에 다시 시도해주세요."}
        )
    except queue.Full:
        logging.error("queue is full")
        return JSONResponse(
            status_code=503,
            content={"message": f"{param} 큐가 가득 차 있습니다. 나중에 다시 시도해주세요."}
        )
@app.get("/")
async def root():
    await asyncio.sleep(1)  # 작업 시뮬레이션
    return {"message": "Hello World"}

@app.get("/long")
async def long_task():
    await asyncio.sleep(5)  # 긴 작업 시뮬레이션
    return {"message": "Long task completed"}

@app.on_event("shutdown")
def shutdown_event():
    job_queue.stop()  # 서버 종료 시 스레드 안전하게 종료

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

