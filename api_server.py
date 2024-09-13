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

from deepl_bot import DeepLBot

app = FastAPI()
MAX_JOB=2

logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    closing:bool=False
    def __init__(self, num_workers):
        self.queue:Queue = Queue(maxsize=num_workers)
        self.num_workers = num_workers
        self.workers = []
        self.bots:List[DeepLBot] = []

    def check(self)->bool:
        logging.info(f"check {self.queue.qsize()}/{self.queue.maxsize}")
        if self.queue.full():
            logging.info("check full")
            raise queue.Full

    def start(self):
        for index in range(self.num_workers):
            worker = threading.Thread(target=self.worker, name=f'job_{index}', daemon=True)
            worker.start()
            self.workers.append(worker)

    def worker(self):
        bot:DeepLBot = DeepLBot(name=threading.current_thread().name)
        self.bots.append(bot)
        while True:
            job=None
            future=None
            try:
                job, future = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue
            finally:
                if self.closing: break

            try:
                result = asyncio.run(job())
                logging.info('go translate')
                translated = bot.translate(result, "ko")
                logging.info(f'translated={str(translated)}')
                result = JSONResponse(content={"message": f"Job completed {translated} successfully"})
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()

    async def add_job(self, job):
        future = asyncio.Future()
        self.queue.put((job, future))
        return await future

    def stop(self):
        logging.info("closing bots")
        for bot in self.bots:
            bot.close()

        logging.info("closing workers")
        self.closing = True
        for worker in self.workers:
            worker.join()  # 스레드가 종료될 때까지 대기

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

