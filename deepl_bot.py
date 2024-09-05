import selenium
import selenium.webdriver
from selenium.webdriver.common.by import By
import time
import traceback

import selenium.webdriver.support
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DeepLBot:
  driver: selenium.webdriver.Chrome

  def __init__(self):
    self.__new_session()

  def __new_session(self):
    options = selenium.webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--lang=ko-KR")
    #options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    #options.add_argument("--remote-debugging-port=9222")
    self.driver = selenium.webdriver.Chrome(options=options)
    self.driver.get("https://www.deepl.com/ko/translator")
    time.sleep(1) # 페이지 로딩 대기
    
  def translate(self, text: str, target_lang: str, source_lang: str = "auto"):
    try:
      return self.__translate(text, target_lang, source_lang)
    except selenium.common.exceptions.ElementNotInteractableException as enie:
      self.close()
      self.__new_session()
      return self.__translate(text, target_lang, source_lang)
    except Exception as e:
      print(f"번역 중 오류 발생: {e}")
      print("스택 트레이스:")
      traceback.print_exc()

      return None

  def __translate(self, text: str, target_lang: str, source_lang: str = "auto")->str:
    input_area = self.driver.find_element(By.NAME, 'source')

    try:
      input_area.send_keys(text)
    except Exception as e:
      print(e)
      print("입력 영역을 찾을 수 없습니다.")
      input_area.send_keys(text)


    print('=========================')
    

    time.sleep(1)
    target_area = self.driver.find_element(By.NAME, 'target')
    if target_area is None:
      raise Exception("번역 결과를 찾을 수 없습니다.")

    translated_len = 0
    translated_text = None

    while True:
      translated_text = target_area.get_attribute("textContent")
      translated_len = len(translated_text)
      if translated_len > 2:
        return translated_text
      time.sleep(0.2)

  def close(self):
    if self.driver is not None:
      self.driver.close()
      self.driver = None

  def __del__(self):
    self.close()

if __name__ == "__main__":
  import threading

  texts = [
    "Hello, world!",
    "This is a test.",
    "I love programming.",
    "Python is a great language.",
    "I am a programmer.",
    "I love programming.",
    "Python is a great language.",
    "I am a programmer.",
  ]

  def translate_texts(texts):
    results = []
    bot = DeepLBot()
    try:
      for text in texts:
        result = bot.translate(text, "ko")
        results.append(result)
    except Exception as e:
      print(f"번역 중 오류 발생: {e}")
    finally:
      bot.close()
    return results

  def run_translation(texts):
    return translate_texts(texts)

  threads = []
  results = []

  for i in range(2):
    thread = threading.Thread(target=lambda: results.append(run_translation(texts[i::2])))
    threads.append(thread)
    thread.start()

  for thread in threads:
    thread.join()

  all_results = [item for sublist in results for item in sublist]
  print("번역 결과:")
  for original, translated in zip(texts, all_results):
    print(f"원문: {original}")
    print(f"번역: {translated}")
    print()

  input('press any key to continue')
