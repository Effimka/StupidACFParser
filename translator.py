import re
import time
import json
from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator
import config

TRANSLATOR = None

def initTranslator():
    global TRANSLATOR
    TRANSLATOR = GoogleTranslator(source="auto", target=config.LANG)

# Регулярка для URL и [shortcode]-блоков
url_pattern = re.compile(r'https?://\S+')
shortcode_pattern = re.compile(r'\[.*?\]')

def should_skip_text(text: str) -> bool:
    """Пропускаем ссылки, URL, пустые строки"""
    if not text or not text.strip():
        return True
    if url_pattern.search(text):
        return True
    if shortcode_pattern.search(text):
        return True
    return False

# === Улучшенный HTML-перевод ===
def translate_html_text(html_text: str) -> str:
    """
    Переводит HTML, пропуская URL, скрипты, шорткоды [....]
    """
    try:
        soup = BeautifulSoup(html_text, "html.parser")
        strings_to_translate = []
        elements = []

        for element in soup.find_all(string=True):
            parent = element.parent
            text = element.strip()
            if not text or parent.name in ["script", "style"]:
                continue
            if should_skip_text(text):
                continue

            strings_to_translate.append(text)
            elements.append(element)

        # === Пакетный перевод ===
        translated_batch = batch_translate(strings_to_translate)

        for el, new_text in zip(elements, translated_batch):
            el.replace_with(NavigableString(new_text))

        return str(soup)

    except Exception:
        if should_skip_text(html_text):
            return html_text
        return TRANSLATOR.translate(html_text)


# === Новый пакетный перевод ===
def batch_translate(texts, delay=0.5):
    """
    Переводит список текстов одним запросом или по частям.
    Возвращает список переведённых строк.
    """
    if not texts:
        return []

    results = []
    batch_size = 10  # Можно увеличить до 20, но Google иногда режет длинные запросы

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        joined = " ||| ".join(batch)

        try:
            translated_joined = TRANSLATOR.translate(joined)
            translated_parts = translated_joined.split(" ||| ")
            if len(translated_parts) != len(batch):
                # fallback на поштучный перевод
                translated_parts = [TRANSLATOR.translate(t) for t in batch]
            results.extend(translated_parts)
        except Exception as e:
            print(f"[translate batch error] {e}, fallback to single mode.")
            for t in batch:
                try:
                    results.append(TRANSLATOR.translate(t))
                except Exception:
                    results.append(t)
            time.sleep(delay)
        time.sleep(delay)  # задержка между пакетами (во избежание бана)

    return results


def translate_json(obj):
    """
    Рекурсивно проходит по JSON, переводит только значения ключей 'text'
    """
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k == "text" and isinstance(v, str):  # перевод строки
                new_dict[k] = translate_html_text(v)
            elif k == "text" and isinstance(v, list):  # массив (например FAQ)
                new_dict[k] = [translate_json(i) for i in v]
            else:
                new_dict[k] = translate_json(v)
        return new_dict

    elif isinstance(obj, list):
        return [translate_json(i) for i in obj]

    else:
        return obj



"""
import glob
import json
from pickle import NONE
import re
from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator
import config
# === Настройки ===
input_file = "blocks.json"
output_file = "blocks_translated.json"

TRANSLATOR = None
def initTranslator():
    global TRANSLATOR
    TRANSLATOR = GoogleTranslator(source="auto", target=config.LANG)

url_pattern = re.compile(r'https?://\S+')

def should_skip_text(text: str) -> bool:
    #Пропускаем ссылки, URL, пустые строки
    if not text or not text.strip():
        return True
    if url_pattern.search(text):
        return True
    return False

def translate_html_text(html_text: str) -> str:
    try:
        soup = BeautifulSoup(html_text, "html.parser")

        for element in soup.find_all(string=True):
            parent = element.parent
            text = element.strip()

            if parent.name in ["script", "style"]:
                continue

            if should_skip_text(text):
                continue

            try:
                translated = TRANSLATOR.translate(text)
                element.replace_with(NavigableString(translated))
            except Exception:
                continue

        return str(soup)
    except Exception:
        # Если это не HTML, просто перевести сам текст
        if should_skip_text(html_text):
            return html_text
        return TRANSLATOR.translate(html_text)

def translate_json(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k == "text" and isinstance(v, str):  # только строки
                new_dict[k] = translate_html_text(v)
            elif k == "text" and isinstance(v, list):  # массивы FAQ внутри
                new_dict[k] = [translate_json(i) for i in v]
            else:
                new_dict[k] = translate_json(v)
        return new_dict

    elif isinstance(obj, list):
        return [translate_json(i) for i in obj]

    else:
        return obj

"""