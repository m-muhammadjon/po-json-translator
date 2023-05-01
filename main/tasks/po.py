import concurrent.futures
import math
import os
import time

import polib
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from googletrans import Translator

from main import karakalpak
from main.models import File
from main.translate import translate_to_cyrillic, translate_to_latin


def translate_po(obj):
    entry = obj["entry"]
    src = obj["src"]
    dest = obj["dest"]
    cnt = obj["index"]
    total = obj["total"]
    pofile_id = obj["pofile_id"]
    # send message to client
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "ws",
        {
            "type": "process",
            "percentage": f"{(cnt / total) * 100}",
            "id": pofile_id,
            "status": "Processing",
        },
    )
    if src == "cry" and dest == "uz":
        entry.msgstr = translate_to_latin(entry.msgid)[1:-1]  # remove quotes
    elif src == "uz" and dest == "cry":
        entry.msgstr = translate_to_cyrillic(entry.msgid)[1:-1]  # remove quotes
    elif (src == "uz" or src == "cry") and dest == "kaa":
        entry.msgstr = karakalpak.translate_to_karakalpak(entry.msgid)
    elif src == "kaa" and dest == "uz":
        entry.msgstr = karakalpak.translate_to_uzbek_latin(entry.msgid)
    elif src == "kaa" and dest == "cry":
        entry.msgstr = karakalpak.translate_karakalpak_to_uzbek_cryillic(entry.msgid)
    else:
        translator = Translator()
        content = entry.msgid
        if content:
            if dest == "cry":
                content_dest = translator.translate(content, src=src, dest="uz")

                entry.msgstr = translate_to_cyrillic(content_dest.text)[1:-1]

            elif dest == "kaa":
                content_dest = translator.translate(content, src=src, dest="uz")

                entry.msgstr = karakalpak.translate_to_karakalpak(content_dest.text)
            else:
                content_dest = translator.translate(content, src=src, dest=dest)

                entry.msgstr = content_dest.text


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 4, "countdown": 5 * 60}, timeout=7200)
def generate_translated_po_task(obj_id):
    start = time.time()
    os.makedirs("media/translates", exist_ok=True)  # create directory if not exists
    obj = File.objects.get(id=obj_id)
    obj.attempts += 1
    obj.status = "Processing"
    obj.save(update_fields=["status", "attempts"])
    if obj.attempts > 4:
        obj.status = "Failed"
        obj.save(update_fields=["status"])
        # send message to client
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            "ws",
            {"type": "process", "status": "Failed", "id": obj_id, "file_link": "", "gen_time": "0.0"},
        )
        return

    src = obj.from_lang  # source language
    dest = obj.to_lang  # destination language
    po = polib.pofile(obj.file.path)  # read po file
    valid_entries = [
        {
            "entry": e,
            "src": src,
            "dest": dest,
            "index": ind,
            "total": len(po),
            "lang_from": obj.get_from_lang_display(),
            "lang_to": obj.get_to_lang_display(),
            "created": str(obj.created_at),
            "pofile_id": obj_id,
        }
        for ind, e in enumerate(po)
    ]  # get valid entries
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        executor.map(translate_po, valid_entries)
    result = str(po)  # convert po data to string
    end = time.time()
    path = f"media/translates/django_{obj.id}.po"  # location to save translated po file
    with open(path, "w") as f:
        f.write(result)  # write to file
    obj.result_file = path
    obj.execution_time = math.ceil(end - start)
    obj.status = "Completed"
    obj.save()

    # send message to client
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "ws",
        {
            "type": "process",
            "status": "Completed",
            "id": obj_id,
            "file_link": path,
            "gen_time": obj.execution_time,
        },
    )
