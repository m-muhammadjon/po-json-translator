import concurrent.futures
import json
import time

import polib
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.cache import cache
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
        f'{obj["user_id"]}',
        {
            "type": "po_process",
            "percentage": f"{(cnt / total) * 100}",
            "cnt": cnt,
            "id": pofile_id,
            "total": total,
            "file_type": "PO",
            "status": "Processing",
            "lang_from": obj["lang_from"],
            "lang_to": obj["lang_to"],
            "created": obj["created"],
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
        entry.msgstr = karakalpak.translate_to_uzbek_cryillic(entry.msgid)
    else:
        translator = Translator()
        content = entry.msgid
        if content:
            print("conten", content)
            print("dest", dest)
            if dest == "cry":
                print("cry")
                content_dest = translator.translate(content, src=src, dest="uz")

                entry.msgstr = translate_to_cyrillic(content_dest.text)[1:-1]

            elif dest == "kaa":
                print("kaa")
                content_dest = translator.translate(content, src=src, dest="uz")

                entry.msgstr = karakalpak.translate_to_karakalpak(content_dest.text)
            else:
                print("else")
                content_dest = translator.translate(content, src=src, dest=dest)

                entry.msgstr = content_dest.text


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 4, "countdown": 5 * 60}, timeout=7200)
def generate_translated_po_task(obj_id):
    print("salom")
    start = time.time()
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
            {"type": "po_process", "status": "Failed", "id": obj_id, "file_link": "", "gen_time": "0.0"},
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
            "user_id": obj.user.id,
            "lang_from": obj.get_from_lang_display(),
            "lang_to": obj.get_to_lang_display(),
            "created": str(obj.created_at),
            "pofile_id": obj_id,
        }
        for ind, e in enumerate(po)
    ]  # get valid entries
    # for entry in valid_entries:
    #     translate_po(entry)
    # multiprocessing
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        executor.map(translate_po, valid_entries)
    result = str(po)  # convert po data to string
    end = time.time()
    path = f"{settings.MEDIA_ROOT}/translates/django_{obj.id}.po"  # location to save translated po file
    with open(path, "w") as f:
        f.write(result)  # write to file
    obj.result_file = f"{settings.HOST}/media/translates/django_{obj.id}.po"
    obj.execution_time = end - start
    obj.status = "Completed"
    obj.save()

    # send message to client
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"{obj.user.id}",
        {
            "type": "po_process",
            "status": "Completed",
            "id": obj_id,
            "file_link": f"{settings.HOST}/media/translates/django_{obj.id}.po",
            "gen_time": obj.execution_time,
        },
    )


def translate(data, **kwargs):
    for key, value in data.items():
        # if value is dict, call translate function recursively
        if isinstance(value, dict):
            translate(value, **kwargs)
        elif isinstance(value, list):
            file_id = kwargs["file_id"]
            src = kwargs["src"]  # source language
            dest = kwargs["dest"]  # destination language
            current_cnt = int(cache.get(f"json_{file_id}"))  # get current count from cache
            total_cnt = int(cache.get(f"json_{file_id}_total"))  # get total count from cache
            cache.set(f"json_{file_id}", current_cnt + 1, 24 * 60 * 60)  # update current count by 1

            # send message to client
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f'{kwargs["user_id"]}',
                {
                    "type": "po_process",
                    "percentage": f"{(current_cnt / total_cnt) * 100}",
                    "cnt": current_cnt,
                    "id": file_id,
                    "total": total_cnt,
                    "file_type": "JSON",
                    "status": "Processing",
                    "lang_from": kwargs["lang_from"],
                    "lang_to": kwargs["lang_to"],
                    "created": kwargs["created"],
                },
            )
            result = []
            for i in value:
                if i:
                    if src == "cry" and dest == "uz":
                        # data[key] = translate_to_latin(i)[1:-1]  # remove quotes
                        result.append(translate_to_latin(i)[1:-1])
                    elif src == "uz" and dest == "cry":
                        # data[key] = translate_to_cyrillic(i)[1:-1]  # remove quotes
                        result.append(translate_to_cyrillic(i)[1:-1])
                    elif (src == "uz" or src == "cry") and dest == "kaa":
                        # data[key] = karakalpak.translate_to_karakalpak(i)
                        result.append(karakalpak.translate_to_karakalpak(i))
                    elif src == "kaa" and dest == "uz":
                        # data[key] = karakalpak.translate_to_uzbek_latin(i)
                        result.append(karakalpak.translate_to_uzbek_latin(i))
                    elif src == "kaa" and dest == "cry":
                        # data[key] = karakalpak.translate_to_uzbek_cryillic(i)
                        result.append(karakalpak.translate_to_uzbek_cryillic(i))
                    else:
                        translator = Translator()
                        content = i
                        if content:
                            content_dest = translator.translate(content, src=src, dest=dest)
                            # data[key] = content_dest.text
                            result.append(content_dest.text)

            data[key] = result
        else:
            file_id = kwargs["file_id"]
            src = kwargs["src"]  # source language
            dest = kwargs["dest"]  # destination language
            current_cnt = int(cache.get(f"json_{file_id}"))  # get current count from cache
            total_cnt = int(cache.get(f"json_{file_id}_total"))  # get total count from cache
            cache.set(f"json_{file_id}", current_cnt + 1, 24 * 60 * 60)  # update current count by 1

            # send message to client
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f'{kwargs["user_id"]}',
                {
                    "type": "po_process",
                    "percentage": f"{(current_cnt / total_cnt) * 100}",
                    "cnt": current_cnt,
                    "id": file_id,
                    "total": total_cnt,
                    "file_type": "JSON",
                    "status": "Processing",
                    "lang_from": kwargs["lang_from"],
                    "lang_to": kwargs["lang_to"],
                    "created": kwargs["created"],
                },
            )

            if value:
                if src == "cry" and dest == "uz":
                    data[key] = translate_to_latin(value)[1:-1]  # remove quotes
                elif src == "uz" and dest == "cry":
                    data[key] = translate_to_cyrillic(value)[1:-1]  # remove quotes
                elif (src == "uz" or src == "cry") and dest == "kaa":
                    data[key] = karakalpak.translate_to_karakalpak(value)
                elif src == "kaa" and dest == "uz":
                    data[key] = karakalpak.translate_to_uzbek_latin(value)
                elif src == "kaa" and dest == "cry":
                    data[key] = karakalpak.translate_to_uzbek_cryillic(value)
                else:
                    translator = Translator()
                    content = value
                    if content:
                        content_dest = translator.translate(content, src=src, dest=dest)
                        data[key] = content_dest.text


def get_total_item_count_json(data, cnt):
    count = cnt
    for key, value in data.items():
        # if value is dict, call get_total_item_count function recursively
        if isinstance(value, dict):
            count += get_total_item_count_json(value, 0)
        else:
            count += 1
    return count


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 4, "countdown": 5 * 60}, timeout=7200)
def generate_translated_json_task(obj_id):
    start = time.time()
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
            {"type": "po_process", "status": "Failed", "id": obj_id, "file_link": "", "gen_time": "0.0"},
        )
        return

    src = obj.from_lang  # source language
    dest = obj.to_lang  # destination language
    f = open(obj.file.path)  # read json file from path
    data = json.loads(f.read())  # convert json data to dict
    total_cnt = get_total_item_count_json(data, 0)  # get total count of dict items
    cache.set(f"json_{obj_id}", 0, 24 * 60 * 60)  # set current count to 0
    cache.set(f"json_{obj_id}_total", total_cnt, 24 * 60 * 60)  # set total count to cache

    # translates dict values
    translate(
        data,
        src=src,
        dest=dest,
        file_id=obj_id,
        user_id=obj.user.id,
        lang_from=obj.get_from_lang_display(),
        lang_to=obj.get_to_lang_display(),
        created=str(obj.created_at),
    )

    result = data
    end = time.time()
    path = f"{settings.MEDIA_ROOT}/translates/{obj.to_lang}_{obj.id}.json"  # location to save translated json file
    with open(path, "w") as f:
        json.dump(result, f, ensure_ascii=False)  # write to file
    obj.result_file = f"{settings.HOST}/media/translates/{obj.to_lang}_{obj.id}.json"
    obj.execution_time = end - start
    obj.status = "Completed"
    obj.save()

    # send message to client
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"{obj.user.id}",
        {
            "type": "po_process",
            "status": "Completed",
            "id": obj_id,
            "file_link": f"{settings.HOST}/media/translates/{obj.to_lang}_{obj.id}.json",
            "gen_time": obj.execution_time,
        },
    )
