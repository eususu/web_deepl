import requests

def translate_text(text, target_lang, auth_key):
    url = "http://localhost:8000/v2/translate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"DeepL-Auth-Key {auth_key}"
    }
    data = {
        "text": text,
        "target_lang": target_lang
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    auth_key = "YOUR_AUTH_KEY"  # 여기에 DeepL API 키를 입력하세요
    target_language = "KO"  # 번역할 언어 (예: EN, DE 등)
    text_to_translate = """The translation function will (by default) try to split the text into sentences before translating. Splitting normally works on punctuation marks (e.g. "." or ";"), though you should not assume that every period will be handled as a sentence separator. This means that you can send multiple sentences as a value of the text parameter. The translation function will separate the sentences and return the whole translated paragraph.
In some cases, the sentence splitting functionality may cause issues by splitting sentences where there is actually only one sentence. This is especially the case if you're using special/uncommon character sequences which contain punctuation. In this case, you can disable sentence splitting altogether by setting the parameter split_sentences to 0. Please note that this will cause overlong sentences to be cut off, as the DeepL API cannot translate overly long sentences. In this case, you should split the sentences manually before submitting them for translation."""

    try:
        result = translate_text(text_to_translate, target_language, auth_key)
        print(result)
    except Exception as e:
        print(e)