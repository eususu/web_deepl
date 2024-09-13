import asyncio
from contextlib import asynccontextmanager
import logging
import queue
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

app = FastAPI()
MAX_JOB=5

logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # 로그 포맷 추가
)

#@asynccontextmanager
#async def lifespan(app):
#    async with app:
#        logging.info("starting~")

import asyncio
import threading
from queue import Queue
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

class JobQueue:
    def __init__(self, num_workers):
        self.queue = Queue(maxsize=num_workers)
        self.num_workers = num_workers
        self.workers = []

    def check(self)->bool:
        if self.queue.full():
            raise queue.Full

    def start(self):
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self.worker, daemon=True)
            worker.start()
            self.workers.append(worker)

    def worker(self):
        while True:
            job, future = self.queue.get()
            try:
                result = asyncio.run(job())
                logging.info(result)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()

    async def add_job(self, job):
        future = asyncio.Future()
        self.queue.put((job, future))
        return await future

job_queue = JobQueue(num_workers=5)

@app.on_event("startup")
def startup_event():
    job_queue.start()

@app.middleware("http")
async def queue_middleware(request, call_next):
    async def job():
        logging.info("running job")
        await asyncio.sleep(5)
        return JSONResponse(content={"message": "Job completed successfully"})

    try:
        job_queue.check()
        response = await job_queue.add_job(job)
        return response
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=503,
            content={"message": "서버가繁합니다. 나중에 다시 시도해주세요."}
        )
    except queue.Full:
        return JSONResponse(
            status_code=503,
            content={"message": "큐가 가득 차 있습니다. 나중에 다시 시도해주세요."}
        )
@app.get("/")
async def root():
    await asyncio.sleep(1)  # 작업 시뮬레이션
    return {"message": "Hello World"}

@app.get("/long")
async def long_task():
    await asyncio.sleep(5)  # 긴 작업 시뮬레이션
    return {"message": "Long task completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

