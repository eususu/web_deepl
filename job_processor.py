import threading
import time
import queue
from queue import Queue
from typing import List, Union
from tqdm import tqdm

from deepl_bot import DeepLBot


class Job:
    def __init__(self, text: str):
        self.text = text
        self.translated_text = None
        self.thread_id = None

    def set_translated_text(self, translated_text: str):
        self.translated_text = translated_text

    def set_thread_id(self, thread_id: int):
        self.thread_id = thread_id

    def get_original_text(self) -> str:
        return self.text

    def get_translated_text(self) -> str:
        return self.translated_text

    def get_thread_id(self) -> int:
        return self.thread_id

class JobProcessor:
  def __init__(self, thread_count:int=5):
    self.bots:List[DeepLBot] = [DeepLBot(str(i)) for i in tqdm(range(thread_count), desc="Create DeepL Bot")]
    print(self.bots)
    self.threads = []
    self.job_queue = Queue()  # Queue로 변경
    self.completed_jobs = Queue()
    self.lock = threading.Lock()
    self.is_running = True

  def process(self, job: Job):
    self.job_queue.put(job)  # Queue에 작업 추가
    if not self.threads:
      self._start_worker_threads()
    return job

  def _start_worker_threads(self):
    for i in tqdm(range(len(self.bots)), desc="Create DeepL Job Thread"):
      thread = threading.Thread(target=self._worker, args=(i,))
      thread.start()
      self.threads.append(thread)

    print(f'# {len(self.bots)} threads are ready.')

  def _worker(self, bot_index):
    bot:DeepLBot = self.bots[bot_index]
    while self.is_running:
      job:Job = None
      try:
          job = self.job_queue.get(timeout=0.1)  # Queue에서 작업 가져오기
      except queue.Empty:
          continue
      
      if job:
        job.set_thread_id(threading.get_ident())
        original_text = job.get_original_text()
        translated_text = bot.translate(original_text, "ko")
        job.set_translated_text(translated_text)
        self.completed_jobs.put(job)
        self.job_queue.task_done()  # 작업 완료 표시
      else:
        time.sleep(0.1)

  def get_completed_job(self)->Union[Job, None]:
    return self.completed_jobs.get() if not self.completed_jobs.empty() else None

  def wait(self):
    for thread in self.threads:
      thread.join()
  
  def close(self):
    self.is_running = False
    for bot in self.bots:
      bot.close()
    self.bots.clear()

if __name__ == "__main__":
  processor = JobProcessor(5)
  jobs = [
    "Hello, world!",
    "This is a test.",
    "I love programming.",
    "Python is a great language.",
    "I am a programmer.",
    "Coding is fun.",
    "Artificial Intelligence is an interesting field.",
    "Software development is a creative work.",
    "Hello, world!",
    "This is a test.",
    "I love programming.",
    "Python is a great language.",
    "I am a programmer.",
    "Coding is fun.",
    "Artificial Intelligence is an interesting field.",
    "Software development is a creative work.",
  ]

  for text in jobs:
    processor.process(Job(text))

  completed_count = 0
  while completed_count < len(jobs):
    completed_job = processor.get_completed_job()
    if completed_job:
      text = completed_job.get_original_text()
      translated_text = completed_job.get_translated_text()
      thread_id = completed_job.get_thread_id()
      print(f"원문: {text}")
      print(f"번역: {translated_text}")
      print(f"스레드 ID: {thread_id}")
      print()
      completed_count += 1
    else:
      time.sleep(0.1)

  processor.close()