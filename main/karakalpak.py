import json
import threading

import requests

from main.translate import translate_to_cyrillic

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def translate_to_karakalpak(text: str) -> str:
    """Translates uzbek text to karakalpak"""
    url = "https://api.from-to.uz/api/v1/translate"

    payload = json.dumps({"body": {"lang_from": "uz", "lang_to": "kaa", "text": f"{text}"}})
    headers = {"Content-Type": "application/json"}
    session = get_session()
    with session.post(url, headers=headers, data=payload) as response:
        result = response.json().get("result")

    return result


def translate_to_uzbek_latin(text: str) -> str:
    """Translates text from karakalpak to uzbek latin"""
    url = "https://api.from-to.uz/api/v1/translate"

    payload = json.dumps({"body": {"lang_from": "kaa", "lang_to": "uz", "text": f"{text}"}})
    headers = {"Content-Type": "application/json"}
    session = get_session()
    with session.post(url, headers=headers, data=payload) as response:
        result = response.json().get("result")

    return result


def translate_karakalpak_to_uzbek_cryillic(text: str) -> str:
    """Translates karakalpak text to uzbek cryillic"""
    result = translate_to_cyrillic(translate_to_uzbek_latin(text))[1:-1]  # remove quotes

    return result
