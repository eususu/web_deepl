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
    options = selenium.webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--lang=ko-KR")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    self.driver = selenium.webdriver.Chrome(options=options)
    self.driver.get("https://www.deepl.com/translator")

  def translate(self, text: str, target_lang: str, source_lang: str = "auto"):
    try:
      return self.__translate(text, target_lang, source_lang)
    except Exception as e:
      print(f"번역 중 오류 발생: {e}")
      print("스택 트레이스:")
      traceback.print_exc()
      return None

  def __translate(self, text: str, target_lang: str, source_lang: str = "auto")->str:
    #input_area = self.driver.find_element(By.NAME, 'source')

    # 입력 영역이 상호작용 가능할 때까지 대기
    wait = WebDriverWait(self.driver, 10)
    input_area = wait.until(EC.presence_of_element_located((By.NAME, 'source')))
    input_area.send_keys(selenium.webdriver.Keys.CONTROL + 'a')
    input_area.send_keys(text)

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
  bot = DeepLBot()
  result = bot.translate("Hello, world!", "ko")
  print(f"번역 결과: {result}")
  v = input('아무 키나 누르세요')
  bot.close()
