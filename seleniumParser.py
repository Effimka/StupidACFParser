import time
import json
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import config
import parserUtils
import os
from translator import translate_json

HEADLESS = False
# Таймауты
DEFAULT_WAIT = 15
# ------------------------------------------
DRIVER = None  # глобальный драйвер
FOLDER = 'Page/'

def create_driver(headless: bool = HEADLESS):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = 'eager'
    # дополнительные опции можно добавить при необходимости
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def login(driver: webdriver.Chrome):
    wait = WebDriverWait(driver, DEFAULT_WAIT)
    driver.get(config.LOGIN_URL)
    # Подстрой под форму сайта: примеры селекторов
    try:
        # Попытка наиболее типичной схемы: input[name="username"], input[name="password"]
        username_el = wait.until(EC.presence_of_element_located((By.NAME, "log")))
        password_el = wait.until(EC.presence_of_element_located((By.NAME, "pwd")))

    except TimeoutException:
        # Пытаться другие распространённые селекторы
        try:
            username_el = wait.until(EC.presence_of_element_located((By.ID, "user_login")))
            password_el = wait.until(EC.presence_of_element_located((By.ID, "user_pass")))
        except TimeoutException:
            raise RuntimeError("Не удалось найти поля логина/пароля — подстрой селекторы в скрипте.")

    username_el.clear()
    username_el.send_keys(config.USERNAME)
    password_el.clear()
    password_el.send_keys(config.PASSWORD)

    # Попытка отправить форму — либо Enter в поле пароля, либо кнопка submit
    password_el.send_keys(Keys.RETURN)

    # Ожидание редиректа / появления элемента, который означает успешный вход
    try:
        # Замените селектор на ожидаемый элемент после логина (например, аватар, logout, dashboard)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        # Можно добавить проверку URL или наличие элемента logout
        time.sleep(1)  # небольшая пауза, чтобы сессия установилась
    except TimeoutException:
        raise RuntimeError("Не удалось подтвердить успешную авторизацию. Проверь логин/пароль или хэндл формы.")


def has_nonempty_text(value):
    if isinstance(value, dict):
        if "text" in value:
            return value["text"] not in (None, "")
        # рекурсивно проверяем все подсловаря
        return any(has_nonempty_text(v) for v in value.values())
    elif isinstance(value, list):
        return any(has_nonempty_text(v) for v in value)
    return False


def open_tabs(driver: webdriver.Chrome, urls: List[str], emit_log=print):
    opened_windows = [driver.current_window_handle]
    for i, url in enumerate(urls):
        # Открываем новую вкладку
        driver.execute_script("window.open('about:blank');")
        # Переключаемся на новую вкладку
        handles = driver.window_handles
        new_handle = [h for h in handles if h not in opened_windows][0]
        driver.switch_to.window(new_handle)
        opened_windows.append(new_handle)
        driver.get(url)
        emit_log(f"[+] Открыл вкладку {i+1}: {url}")
        # Небольшая пауза между загрузками — чтобы не ударять сервер слишком быстро
        time.sleep(0.5)
    # Возвращаем список всех открытых окон в порядке открытия
    return driver.window_handles


def parse_in_current_tab(driver: webdriver.Chrome, emit_log=print):
    rows = WebDriverWait(driver, DEFAULT_WAIT).until( lambda d: d.find_elements(By.CSS_SELECTOR, ".acf-row") )
    blocks = []

    for row in rows:
        block = {}
        title_el, title_text = parserUtils.parse_title(row)
        block["title"] = {"element": title_el, "text": title_text}

        btnText_el, btnText_text = parserUtils.parse_icon_menu(row)
        block["icon_menu"] = {"element": btnText_el, "text": btnText_text}

        content_el, content_data = parserUtils.parse_content(row)
        block["content"] = {"element": content_el, "text": content_data}

        collum_el, collum_data = parserUtils.parse_collum(row)
        block["collum"] = {"element": collum_el, "text": collum_data}

        collumImg_el, collumImg_data = parserUtils.parse_collum_img(row)
        block["collumImg"] = {"element": collumImg_el, "text": collumImg_data}

        collumImg_el, collumImg_data = parserUtils.parse_column_game(row)
        block["collumGame"] = {"element": collumImg_el, "text": collumImg_data}

        btnText_el, btnText_text = parserUtils.parse_button_text(row)
        block["button_text"] = {"element": btnText_el, "text": btnText_text}

        btnText_el, btnText_text = parserUtils.parse_bonus_block_text(row)
        block["bonus_block"] = {"element": btnText_el, "text": btnText_text}

        anchor_el, anchor_text = parserUtils.parse_decor(row)
        block["decor"] = {"element": anchor_el, "text": anchor_text}

        anchor_el, anchor_text = parserUtils.parse_anchor(row)
        block["anchor"] = {"element": anchor_el, "text": anchor_text}

        if has_nonempty_text(block):
            blocks.append(block)

    emit_log(f"Найдено {len(blocks)} блоков")
    return blocks


def StartSelenim(emit_log=print):
    RemoveJsonFile()
    global DRIVER
    urls = config.TARGET_URLS.copy()

    if not urls:
        raise ValueError("Нет URL для открытия — укажи TARGET_URLS или TARGET_URL_TEMPLATE + N_TABS.")

    emit_log("Создается драйвер через который будет выполняться вход")
    DRIVER = create_driver()
    emit_log("Драйвер создан успешно")
    emit_log("Входим в админку")
    login(DRIVER)
    emit_log("Удачно вошли в админку")

    open_tabs(DRIVER, urls, emit_log)
    time.sleep(5)


def ParseData(emit_log=print):
     # Проход по каждой вкладке и обработка
    for idx, handle in enumerate(DRIVER.window_handles):
        DRIVER.switch_to.window(handle)
        current_url = DRIVER.current_url
        if current_url == config.LOGIN_URL:
            continue
        emit_log(f"[{idx+1}] Собираю данные из вкладки — {current_url}")
        try:
            blocks = parse_in_current_tab(DRIVER, emit_log)
            with open(f'Page/{idx+1}_page_blocks.json', 'w', encoding='utf-8') as f:
                json.dump(blocks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            emit_log(f"Ошибка при обработке вкладки {current_url}: {e}")
            raise


def DriverShutdown(emit_log=print):
    if not HEADLESS:
        emit_log("Оставлю браузер открытым 25 секунд для проверки...")
        time.sleep(25)
    DRIVER.quit();


def StarTranslate(emit_log=print):
    MakeTranslatedJsons(emit_log)
    try:
        for idx, handle in enumerate(DRIVER.window_handles):
            DRIVER.switch_to.window(handle)
            current_url = DRIVER.current_url
            if current_url == config.LOGIN_URL:
                continue
            
            filename = f"{idx+1}_page_blocks.json_translated.json"
            filepath = os.path.join(f'{FOLDER}translate/', filename)
            if not os.path.exists(filepath):
                emit_log(f"Файл {filename} для не найден для ссылки {current_url}")
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            emit_log(f'Заполняем страницу {filename}')
            for item in data:
                for field_name in ["title", "icon_menu", "content", "collum", "collumImg", "collumGame", "button_text", "bonus_block", "decor", "anchor"]:
                    field = item.get(field_name)
                    if not field:
                        continue
                    process_text_field(DRIVER, field.get("element"), field.get("text"), emit_log)
        
    except Exception as e:
        emit_log(f"Не удалось записать перевод для  {current_url}. Ошибка: {e}")

   

def RemoveJsonFile():
    for filename in os.listdir(FOLDER):
        file_path = os.path.join(FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Не удалось удалить {file_path}. Ошибка: {e}")
    os.makedirs(f"{FOLDER}translate", exist_ok=True)


def MakeTranslatedJsons(emit_log=print):
    for filename in os.listdir(FOLDER):
        file_path = os.path.join(FOLDER, filename)
        try:
        
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            emit_log(f'Переводим файл - {filename}')
            translated_data = [translate_json(block) for block in data]
            emit_log(f'Сохраняем перевод файла')

            with open(f'{FOLDER}translate/{filename}_translated.json', "w", encoding="utf-8") as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=4)
        
        except Exception as e:
            emit_log(f"Не удалось удалить {file_path}. Ошибка: {e}")


def smart_find(driver, element_info, emit_log=print):
    by = element_info.get("by")
    selector = element_info.get("selector")

    if by == "id":
        return driver.find_element(By.ID, selector)

    if by == "css selector":
        return driver.find_element(By.CSS_SELECTOR, selector)

    if by == "xpath":
        print(driver.find_element(By.XPATH, selector))
        return driver.find_element(By.XPATH, selector)

    if by == "html":
        # если вдруг сохранился outerHTML, пробуем вытащить id
        import re
        match = re.search(r'id="([^"]+)"', selector)
        if match:
            return driver.find_element(By.ID, match.group(1))

    raise ValueError(f"Не удалось восстановить элемент: {element_info}")


def smart_insert(driver, element, text, emit_log=print):
    # Если element — список (возможно несколько textarea)
    if isinstance(element, list):
        for el in element:
            if not el.get_attribute("disabled"):
                element = el
                break
        else:
            emit_log("Все элементы disabled, ничего не вставляем")
            return

    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].focus();", element)
        time.sleep(0.2)

        if element.get_attribute("disabled"):
            emit_log(f"Элемент {element} выключен, пробуем JS/TinyMCE")
            editor_id = element.get_attribute("id")
            if editor_id:
                driver.execute_script("""
                    if (typeof tinymce !== 'undefined' && tinymce.get(arguments[0])) {
                        tinymce.get(arguments[0]).setContent(arguments[1]);
                    } else {
                        document.getElementById(arguments[0]).value = arguments[1];
                    }
                """, editor_id, text)
            return

        element.clear()
        element.send_keys(text)

    except Exception as e:
        emit_log(f"⚠️ Не удалось вставить через send_keys, пробуем JS/TinyMCE")
        editor_id = element.get_attribute("id")
        driver.execute_script("""
            if (typeof tinymce !== 'undefined' && tinymce.get(arguments[0])) {
                tinymce.get(arguments[0]).setContent(arguments[1]);
            } else {
                document.getElementById(arguments[0]).value = arguments[1];
            }
        """, editor_id, text)


def smart_find_first_interactive(driver, element_info_list, emit_log=print):
    """
    element_info_list: может быть один элемент или список элементов (локаторы)
    возвращает первый элемент, который не disabled
    """
    if not isinstance(element_info_list, list):
        element_info_list = [element_info_list]

    for info in element_info_list:
        try:
            el = smart_find(driver, info, emit_log)
            if not el.get_attribute("disabled"):
                return el
        except Exception:
            continue

    emit_log("⚠️ Все элементы disabled или не найдены")
    return None


def process_text_field(driver, element_info, text_data, emit_log=print):
    if isinstance(text_data, str):
        el = smart_find_first_interactive(driver, element_info, emit_log)
        if el:
            smart_insert(driver, el, text_data, emit_log)

    elif isinstance(text_data, list):
        for subitem in text_data:
            for subfield in ["question", "answer"]:
                if subfield in subitem:
                    sub_el_info = subitem[subfield].get("element")
                    sub_text = subitem[subfield].get("text", "")
                    el = smart_find_first_interactive(driver, sub_el_info, emit_log)
                    if el:
                        smart_insert(driver, el, sub_text)
            for subfield in ["Cell"]:
                if subfield in subitem:
                    print(f'subfield : {subfield} in subitem')
                    sub_el_info = subitem[subfield].get("element")
                    sub_text = subitem[subfield].get("text", "")
                    print(f'sub_el_info : {sub_el_info} in sub_text : {sub_text}')
                    el = smart_find_first_interactive(driver, sub_el_info, emit_log)
                    if el:
                        smart_insert(driver, el, sub_text)
            for subfield in ["collum_title", "collum_text"]:
                if subfield in subitem:
                    sub_el_info = subitem[subfield].get("element")
                    sub_text = subitem[subfield].get("text", "")
                    el = smart_find_first_interactive(driver, sub_el_info, emit_log)
                    if el:
                        smart_insert(driver, el, sub_text)
            for subfield in ["bonus_block_title", "bonus_block_size", "bonus_block_desc", "bonus_block_btn"]:
                if subfield in subitem:
                    sub_el_info = subitem[subfield].get("element")
                    sub_text = subitem[subfield].get("text", "")
                    el = smart_find_first_interactive(driver, sub_el_info, emit_log)
                    if el:
                        smart_insert(driver, el, sub_text)


    else:
        print(f"[DEBUG] Тип данных: {type(text_data)} | Содержимое: {text_data}")
        emit_log(f"⚠️ Неподдерживаемый тип текста: {type(text_data)}")


