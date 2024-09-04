import selenium
from selenium.webdriver.common.by import By
import time

class DeepLBot:
  driver: selenium.webdriver.Chrome

  def __init__(self):
    options = selenium.webdriver.ChromeOptions()
    options.add_argument("--headless")
    self.driver = selenium.webdriver.Chrome(options=options)
    self.driver.get("https://www.deepl.com/translator")

  def translate(self, text: str, target_lang: str, source_lang: str = "auto"):
    try:
      self.__translate(text, target_lang, source_lang)
    except Exception as e:
      print(e)
      print(f"번역 중 오류 발생: {e}")
      return None

  def __translate(self, text: str, target_lang: str, source_lang: str = "auto"):
    print("번역 시작")
    input_area = self.driver.find_element(By.NAME, 'source')
    print("입력 준비")
    input_area.send_keys(selenium.webdriver.Keys.CONTROL + 'a')
    print("입력 완료")
    input_area.send_keys(text)
    print("입력 완료1")

    time.sleep(1)
    print("번역 중...")
    target_area = self.driver.find_element(By.NAME, 'target')
    print("번역 완료")
    if target_area is None:
      raise Exception("번역 결과를 찾을 수 없습니다.")
    translated_text = target_area.text
    print(translated_text)

    return translated_text

  def close(self):
    if self.driver is not None:
      self.driver.close()
      self.driver = None

  def __del__(self):
    self.close()

if __name__ == "__main__":
  bot = DeepLBot()
  print(bot.translate("Hello, world!", "ko"))
  bot.close()
