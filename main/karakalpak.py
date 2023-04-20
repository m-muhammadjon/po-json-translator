import json
import threading

import requests

from main.translate import translate_to_cyrillic

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def translate_to_karakalpak(text):
    url = "https://api.from-to.uz/api/v1/translate"

    payload = json.dumps({"body": {"lang_from": "uz", "lang_to": "kaa", "text": f"{text}"}})
    headers = {"Content-Type": "application/json"}
    session = get_session()
    result = ""
    with session.post(url, headers=headers, data=payload) as response:
        result = response.json().get("result")

    return result


def translate_to_uzbek_latin(text):
    url = "https://api.from-to.uz/api/v1/translate"

    payload = json.dumps({"body": {"lang_from": "kaa", "lang_to": "uz", "text": f"{text}"}})
    headers = {"Content-Type": "application/json"}
    session = get_session()
    result = ""
    with session.post(url, headers=headers, data=payload) as response:
        result = response.json().get("result")

    return result


def translate_karakalpak_to_uzbek_cryillic(text):
    """
    Translates karakalpak text to uzbek cryillic
    :param text:
    :return: str
    """
    result = translate_to_cyrillic(translate_to_uzbek_latin(text))[1:-1]  # remove quotes

    return result
