from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

TITLE_EL_ARR = [ 'field_640c5b8d20ccd', 'field_640c6063bba51', 'field_640b9093230e3', 'field_6867d4520b00e', 'field_684c251d0a653', 'field_68546226b5741', 'field_6854089bb995c', 'field_6867b3142a6bf', 'field_640c963ce4abf', 'field_641090657015c' ]
CONTENT_EL_MAP = {
    'base' : [ 'field_640c5b8d2bdba', 'field_6867d45216058', 'field_684c31edef5f4', 'field_684c251d157d1', 'field_6854628f0ff99', 'field_68540914b995e' ],
    'faq' : {
        'repeater' : 'div[data-key="field_640b910fb16b0"] .acf-repeater',
         'faq_rows' : 'tr.acf-row:not(.acf-clone)',
         'question_input' : 'input[name*="[field_640b9118b16b1]"]',
         'answer_textarea' : 'textarea[name*="[field_640b911eb16b2]"]'    
    },
}
#COLUMN_EL_ARR = 
BUTTON_EL_ARR = [ 'field_640c5b8d42263', 'field_684c3257ef5f6', 'field_684c251d1cc1a', 'field_6854095ab995f', 'field_640c9825498f3' ]
DECOR_EL_ARR = [ 'field_6867c0727114b' ]
ANCHOR_EL_ARR = [ 'field_684c202428761', 'field_684c229243962', 'field_684c251d27bb9', 'field_68546226c7c7b', 'field_6867d45224b20', 'field_684c21f42786d', 'field_6867b31444381' ]


def get_locator(el: WebElement) -> dict:
    if not el:
        return None
    try:
        el_id = el.get_attribute("id")
        if el_id:
            return {"by": "id", "selector": el_id}

        name_attr = el.get_attribute("name")
        if name_attr:
            # часто ACF имеет уникальный name
            return {"by": "css selector", "selector": f'[name="{name_attr}"]'}

        # запасной вариант — относительный XPATH
        xpath = el.get_attribute("xpath") if hasattr(el, "get_attribute") else None
        if xpath:
            return {"by": "xpath", "selector": xpath}

        class_attr = el.get_attribute("class") or ""
        if "acf-table-body-cont" in class_attr:
            text = el.text.strip()
            if text:
                xpath = f'//div[contains(@class, "acf-table-body-cont") and normalize-space()="{text}"]'
                return {"by": "xpath", "selector": xpath}

        # если ничего нет — хотя бы outerHTML, но с пометкой
        return {"by": "html", "selector": el.get_attribute("outerHTML")}
    except Exception:
        return {"by": "unknown", "selector": "<detached>"}


def parse_title(row: WebElement):
    title_elements = []
    for field in TITLE_EL_ARR:
        try:
            els = row.find_elements(By.CSS_SELECTOR, f'input[name*="[{field}]"]')
            title_elements.extend(els)
        except:
            continue
    # берём текст первого активного
    for el in title_elements:
        if not el.get_attribute("disabled"):
            return get_locator(el), el.get_attribute("value").strip()
    return None, ''


def parse_table(row: WebElement, driver):
    try:
        table_wrap = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_684c257dbcc8a"], div.acf-field[data-type="table"]')
        table_locator = None
        for table in table_wrap:
            cells = table.find_elements(By.CSS_SELECTOR, ".acf-table-body-cell .acf-table-body-cont")
            cell_data = []
            for cell in cells:
                text = driver.execute_script("return arguments[0].textContent;", cell).strip()
                if not text:
                    continue
                cell_data.append({
                    "Cell" : {
                        "element": get_locator(cell),
                        "text": text
                    }
                })
                if not table_locator:
                        table_locator = get_locator(table)
        
        if cell_data:
            return table_locator, cell_data
        return None, None
    except Exception:
        return None, None


def parse_collum(row: WebElement):
    table_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-name="column"], div.acf-field[data-key="field_68546226c0777"]')
    all_data = []
    table_locator = None
    for table_body in table_bodies:
        try:
            title_inputs = table_body.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-name="title"] input') 
            text_inputs = table_body.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-name="text"] input')

            for title_input, text_input in zip(title_inputs, text_inputs):
                title = title_input.get_attribute("value").strip() if not title_input.get_attribute("disabled") else ''
                text = text_input.get_attribute("value").strip() if not text_input.get_attribute("disabled") else ''

                if title or text:
                    all_data.append({
                        "collum_title": {"element": get_locator(title_input), "text": title},
                        "collum_text": {"element": get_locator(text_input), "text": text}
                    })
                    if not table_locator:
                        table_locator = get_locator(table_body)
        
        except Exception:
            continue 
    if all_data:
        return table_locator, all_data

    return None, None


def parse_collum_img(row: WebElement):
    table_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-name="column_adv"], div.acf-field[data-key="field_6867d4521d639"]')
    if not table_bodies:
        table_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-name="column_game"], div.acf-field[data-key="field_6867b3143ce18"]')
    all_data = []
    table_locator = None
    for table_body in table_bodies:
        try:
            title_inputs = table_body.find_elements(By.CSS_SELECTOR, f'input[name*="[field_6867d4523736d]"]')
            if not title_inputs:
                title_inputs = table_body.find_elements(By.CSS_SELECTOR, f'input[name*="[field_6867b314534a4]"]')

            text_inputs = table_body.find_elements(By.CSS_SELECTOR, f'textarea[name*="[field_6867d4523ae3d]"]')
            if not text_inputs:
                text_inputs = table_body.find_elements(By.CSS_SELECTOR, f'textarea[name*="[field_6867bff571149]"]')


            for title_input, text_input in zip(title_inputs, text_inputs):
                title = title_input.get_attribute("value").strip() if not title_input.get_attribute("disabled") else ''
                text = text_input.get_attribute("value").strip() if not text_input.get_attribute("disabled") else ''

                if title or text:
                    all_data.append({
                        "collum_title": {"element": get_locator(title_input), "text": title},
                        "collum_text": {"element": get_locator(text_input), "text": text}
                    })
                    if not table_locator:
                        table_locator = get_locator(table_body)
        
        except Exception:
            continue 
    if all_data:
        return table_locator, all_data

    return None, None


def parse_column_game(row: WebElement):
    try:
        game_blocks = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_6867b3143ce18"]')
        if not game_blocks:
            game_blocks = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-name="column_game"][data-type="repeater"]')

        all_data = []
        table_locator = None

        for block in game_blocks:
            rows = block.find_elements(By.CSS_SELECTOR, "tr.acf-row")
            print(rows)
            if not rows:
                continue

            for row_el in rows:
                inputs = row_el.find_elements(By.CSS_SELECTOR, "input[type='text']")
                name = row_el.find_element(By.CSS_SELECTOR, '[data-name="game_name"] input[type="text"]')
                #name = inputs[0].get_attribute("value").strip()
                #btn_text = inputs[1].get_attribute("value").strip()
                btn = row_el.find_element(By.CSS_SELECTOR, '[data-name="game_link_title"] input[type="text"]')

                name_text = name.get_attribute("value").strip()
                btn_text = btn.get_attribute("value").strip()
                if name_text or btn_text:
                    all_data.append({
                        "collum_title": { "element": get_locator(name), "text": name_text },
                        "collum_text": { "element": get_locator(btn), "text": btn_text },
                    })

                    if not table_locator:
                        table_locator = get_locator(block)

        if all_data:
            return table_locator, all_data

    except Exception as e:
        print("Ошибка в parse_icon_menu:", e)

    return None, None


def parse_content(row: WebElement):
    # Проверяем базовые поля
    for field in CONTENT_EL_MAP['base']:
        try:
            # находим все textarea по селектору
            textareas = row.find_elements(By.CSS_SELECTOR, f'textarea[name*="[{field}]"]')
            for el in textareas:
                # берём первый не-disabled
                if not el.get_attribute("disabled"):
                    content_text = el.get_attribute("value").strip()
                    return get_locator(el), content_text
        except Exception:
            continue

    # Если base не сработало — пробуем FAQ
    try:
        faq_map = CONTENT_EL_MAP['faq']
        repeater_el = row.find_element(By.CSS_SELECTOR, faq_map['repeater'])
        faq_rows = repeater_el.find_elements(By.CSS_SELECTOR, faq_map['faq_rows'])
        faq_items = []

        for faq_row in faq_rows:
            try:
                question_el = faq_row.find_element(By.CSS_SELECTOR, faq_map['question_input'])
                answer_el = faq_row.find_element(By.CSS_SELECTOR, faq_map['answer_textarea'])

                # Берём только активные элементы
                question_text = question_el.get_attribute("value").strip() if not question_el.get_attribute("disabled") else ''
                answer_text = answer_el.get_attribute("value").strip() if not answer_el.get_attribute("disabled") else ''

                if question_text or answer_text:
                    faq_items.append({
                        "question": {"element": get_locator(question_el), "text": question_text},
                        "answer": {"element": get_locator(answer_el), "text": answer_text}
                    })
            except Exception:
                continue

        if faq_items:
            return get_locator(repeater_el), faq_items
    except Exception:
        pass

    return None, None


def parse_button_text(row: WebElement):
    btn_elements = []
    for field in BUTTON_EL_ARR:
        try:
            els = row.find_elements(By.CSS_SELECTOR, f'input[name*="[{field}]"]')
            btn_elements.extend(els)
        except:
            continue
    for el in btn_elements:
        if not el.get_attribute("disabled"):
            return get_locator(el), el.get_attribute("value").strip()
    return None, ''


def parse_bonus_block_text(row: WebElement):
    accordion_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_641c9292b0a24"]')
    if not accordion_bodies:
            accordion_bodies = row.find_elements(By.CSS_SELECTOR, 'div[data-name="section_page"][data-type="repeater"]')

    all_data = []
    main_locator = None
    for body in accordion_bodies:
        try:
            title_inputs = body.find_elements(By.CSS_SELECTOR, f'input[name*="[field_68540af7b9963]"]')
            bonusSize_inputs = body.find_elements(By.CSS_SELECTOR, f'input[name*="[field_68540b56b9964]"]') 
        
            bonusDesc_inputs = body.find_elements(By.CSS_SELECTOR, f'input[name*="[field_68540b7fb9965]"])')
            btnText_inputs = body.find_elements(By.CSS_SELECTOR, f'input[name*="[field_68540ba2b9966]"])')


            for title_input, bonusSize_input, bonusDesc_input, btnText_input in zip(title_inputs, bonusSize_inputs, bonusDesc_inputs, btnText_inputs):
                title = title_input.get_attribute("value").strip() if not title_input.get_attribute("disabled") else ''
                size = bonusSize_input.get_attribute("value").strip() if not bonusSize_input.get_attribute("disabled") else ''
                desc = bonusDesc_input.get_attribute("value").strip() if not bonusDesc_input.get_attribute("disabled") else ''
                btn = btnText_input.get_attribute("value").strip() if not btnText_input.get_attribute("disabled") else ''


                if title or size or desc or btn:  
                    all_data.append({
                        "bonus_block_title": {"element": get_locator(title_input), "text": title},
                        "bonus_block_size": {"element": get_locator(bonusSize_input), "text": size},
                        "bonus_block_desc": {"element": get_locator(bonusDesc_input), "text": desc},
                        "bonus_block_btn": {"element": get_locator(btnText_input), "text": btn}
                    })
                    if not main_locator:
                        main_locator = get_locator(body)
        
        except Exception:
            continue 
    if all_data:
        return main_locator, all_data

    return None, None


def parse_block(row: WebElement):
    all_data = []
    main_locator = None

    # несколько accordion блоков
    block_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_641c92a039bb4"]')
    print(f"Found {len(block_bodies)} accordion bodies")

    for body in block_bodies:
        try:
            repeater = body.find_element(By.CSS_SELECTOR, 'div.acf-field-repeater[data-key="field_640c64cf07fe4"]')

            # ищем все строки в таблице
            rows = repeater.find_elements(By.CSS_SELECTOR, 'table.acf-table tr.acf-row')
            print(f"  Found {len(rows)} rows in repeater")

            for r in rows:
                title_input = r.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c64f107fe6]"]')
                text_input = r.find_elements(By.CSS_SELECTOR, 'textarea[name*="[field_64536ce155402]"]')
                btnText_input = r.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c651407fea]"]')

                listText = r.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c650007fe8]"]')

                if text_input or btnText_input:
                    for title_in, text_in, btnT_in in zip(title_input, text_input, btnText_input):
                        title = title_in.get_attribute("value") or ""
                        text = text_in.get_attribute("value") or ""
                        btn = btnT_in.get_attribute("value") or ""

                        if title.strip() or text.strip() or btn.strip():
                            all_data.append({
                                "block_title": {"element": get_locator(title_in), "text": title.strip()},
                                "block_text": {"element": get_locator(text_in), "text": text.strip()},
                                "block_btn": {"element": get_locator(btnT_in), "text": btn.strip()}
                            })
                elif listText:
                    for textIn in listText:
                        text = textIn.get_attribute("value") or ""

                        if text.strip():
                            all_data.append({
                                "block_text": {"element": get_locator(textIn), "text": text.strip()},
                            })

                
            if not main_locator:
                main_locator = get_locator(body)

            
        
        except Exception as e:
            print(f"Ошибка при парсинге блока: {e}")
            continue

    return (main_locator, all_data) if all_data else (None, None)


def parse_block_promo(row: WebElement):
    block_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_643d44a25561c"]')
    all_data = []
    main_locator = None

    for body in block_bodies:
        # Парсим все заголовки
        title1_inputs = body.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c90780c8a2]"]')
        title2_inputs = body.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c90830c8a3]"]')
        title3_inputs = body.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c90840c8a4]"]')

        max_len = max(len(title1_inputs), len(title2_inputs), len(title3_inputs))
        for i in range(max_len):
            title1_input = title1_inputs[i] if i < len(title1_inputs) else None
            title2_input = title2_inputs[i] if i < len(title2_inputs) else None
            title3_input = title3_inputs[i] if i < len(title3_inputs) else None

            title1 = title1_input.get_attribute("value").strip() if title1_input and not title1_input.get_attribute("disabled") else ''
            title2 = title2_input.get_attribute("value").strip() if title2_input and not title2_input.get_attribute("disabled") else ''
            title3 = title3_input.get_attribute("value").strip() if title3_input and not title3_input.get_attribute("disabled") else ''

            if title1 or title2 or title3:
                all_data.append({
                    "title1": {"element": get_locator(title1_input) if title1_input else None, "text": title1},
                    "title2": {"element": get_locator(title2_input) if title2_input else None, "text": title2},
                    "title3": {"element": get_locator(title3_input) if title3_input else None, "text": title3},
                })

                if not main_locator:
                    main_locator = get_locator(body)

    if all_data:
        return main_locator, all_data

    return None, None


def parse_block_advantages(row: WebElement):
    block_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_643d44a25561c"]')
    all_data = []
    main_locator = None

    for body in block_bodies:
        try:
            title1_inputs = body.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c88d683da9]"]')
            title2_inputs = body.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c88ee83daa]"]')
            title3_inputs = body.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c88f683dab]"]')
            btnText_inputs = body.find_elements(By.CSS_SELECTOR, 'input[name*="[field_640c899f83dad]"]')

            for title1_input, title2_input, title3_input, btnText_input in zip(title1_inputs, title2_inputs, title3_inputs, btnText_inputs):
                title1 = title1_input.get_attribute("value").strip() if not title1_input.get_attribute("disabled") else ''
                title2 = title2_input.get_attribute("value").strip() if not title2_input.get_attribute("disabled") else ''
                title3 = title3_input.get_attribute("value").strip() if not title3_input.get_attribute("disabled") else ''
                btn = btnText_input.get_attribute("value").strip() if not btnText_input.get_attribute("disabled") else ''

                if title1 or title2 or title3 or btn:  
                    all_data.append({
                        "title1": {"element": get_locator(title1_input), "text": title1},
                        "title2": {"element": get_locator(title2_input), "text": title2},
                        "title3": {"element": get_locator(title3_input), "text": title3},
                        "block_btn": {"element": get_locator(btnText_input), "text": btn}
                    })

                    if not main_locator:
                        main_locator = get_locator(body)
        
        except Exception:
            continue 

    if all_data:
        return main_locator, all_data

    return None, None


def parse_anchor(row: WebElement):
    anchor_elements = []
    for field in ANCHOR_EL_ARR:
        try:
            els = row.find_elements(By.CSS_SELECTOR, f'input[name*="[{field}]"]')
            anchor_elements.extend(els)
        except:
            continue
    for el in anchor_elements:
        if not el.get_attribute("disabled"):
            return get_locator(el), el.get_attribute("value").strip()
    return None, ''


def parse_decor(row: WebElement):
    decor_elements = []
    for field in DECOR_EL_ARR:
        try:
            els = row.find_elements(By.CSS_SELECTOR, f'input[name*="[{field}]"]')
            decor_elements.extend(els)
        except:
            continue
    for el in decor_elements:
        if not el.get_attribute("disabled"):
            return get_locator(el), el.get_attribute("value").strip()
    return None, ''


def parse_bonus_section(row: WebElement):
    try:
        table_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_64108fe3b696e"]')
        all_data = []
        table_locator = None

        for table_body in table_bodies:
            # Каждая строка в repeater-е
            rows = table_body.find_elements(By.CSS_SELECTOR, 'table.acf-table tr.acf-row')

            for r in rows:
                # безопасные поиски, чтобы не падало
                title_el = r.find_elements(By.CSS_SELECTOR, 'input[name*="[field_64108ff4b6970]"]')
                text_el = r.find_elements(By.CSS_SELECTOR, 'input[name*="[field_64108ffab6971]"]')

                max_len = max(len(title_el), len(text_el))
                for i in range(max_len):
                    title_input = title_el[i] if i < len(title_el) else None
                    text_input = text_el[i] if i < len(text_el) else None

                    title = title_input.get_attribute("value").strip() if title_input and not title_input.get_attribute("disabled") else ''
                    text = text_input.get_attribute("value").strip() if text_input and not text_input.get_attribute("disabled") else ''

                    # добавляем только непустые строки
                    if title or text:
                        all_data.append({
                            "bonus_title": {"element": get_locator(title_input) if title_input else None, "text": title},
                            "bonus_text": {"element": get_locator(text_input) if text_input else None, "text": text},
                        })
                        if not table_locator:
                            table_locator = get_locator(table_body)

        if all_data:
            return table_locator, all_data

    except Exception as e:
        print("Ошибка в parse_bonus_section:", e)

    return None, None


def parse_icon_menu(row: WebElement):
    try:
        # Ищем repeater-группы глубоко внутри
        table_bodies = row.find_elements(By.CSS_SELECTOR, 'div.acf-field[data-key="field_68544aa99fa6d"]')
        if not table_bodies:
            table_bodies = row.find_elements(By.CSS_SELECTOR, 'div[data-name="menu_item"][data-type="repeater"]')

        all_data = []
        table_locator = None

        for table_body in table_bodies:
            # каждая строка таблицы
            rows = table_body.find_elements(By.CSS_SELECTOR, 'tr.acf-row:not(.acf-clone)')
            for r in rows:
                title_input = r.find_element(By.CSS_SELECTOR, 'td[data-name="title"] input')
                text_input = r.find_element(By.CSS_SELECTOR, 'td[data-name="text"] input')

                title = title_input.get_attribute("value").strip()
                text = text_input.get_attribute("value").strip()

                if title or text:
                    all_data.append({
                        "collum_title": {"element": get_locator(title_input), "text": title},
                        "collum_text": {"element": get_locator(text_input), "text": text},
                    })
                    if not table_locator:
                        table_locator = get_locator(table_body)
        if all_data:
            return table_locator, all_data

    except Exception as e:
        print("Ошибка в parse_icon_menu:", e)

    return None, None