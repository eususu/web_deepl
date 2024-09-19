import requests

def translate_text(text, target_lang, auth_key):
    url = "http://localhost:8000/v2/translate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "auth_key": auth_key,
        "text": text,
        "target_lang": target_lang
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")
# 사용 예시
if __name__ == "__main__":
    auth_key = "YOUR_AUTH_KEY"  # 여기에 DeepL API 키를 입력하세요
    text_to_translate = "airplane"
    target_language = "KO"  # 번역할 언어 (예: EN, DE 등)

    try:
        result = translate_text(text_to_translate, target_language, auth_key)
        print(result)
    except Exception as e:
        print(e)