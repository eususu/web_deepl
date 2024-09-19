from queue import Queue
import asyncio
import logging
import queue
import threading
from typing import List

from fastapi.responses import JSONResponse
from _types import TranslationRequest, TranslationResponse, Translations
from deepl_bot import DeepLBot

class JobQueue(object):
  closing:bool=False
  def __init__(self, num_workers):
    self.queue:Queue = Queue(maxsize=num_workers)
    self.num_workers = num_workers
    self.workers:List[threading.Thread] = []
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
        job, future = self.queue.get()
      except queue.Empty:
        continue
      finally:
        if self.closing: break

      try:
        result:TranslationRequest = asyncio.run(job())
        logging.info('go translate')
        translated = bot.translate(result.text, "ko")
        logging.info(f'translated={str(translated)}')

        response = TranslationResponse(
          translations=[
          Translations(
          detected_source_language="EN",
          text=translated,
          billed_characters=0)
          ]
        )
        future.set_result(response)
      except Exception as e:
        future.set_exception(e)
      finally:
        self.queue.task_done()

  async def add_job(self, job):
    future = asyncio.Future()
    print(self.queue)
    self.queue.put((job, future))
    return await future

  def stop(self):
    logging.info("closing bots")
    for bot in self.bots:
      try:
        bot.close()
      except Exception as e:
        logging.error(e)

    logging.info("closing workers")
    self.closing = True
    for worker in self.workers:
      worker.join(timeout=1)  # 1초 대기 후 강제 종료
      if worker.is_alive():
        logging.warning(f"Worker {worker.name} did not terminate in time. Forcing termination.")