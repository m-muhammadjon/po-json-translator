from main.tasks import (generate_translated_json_task,
                        generate_translated_po_task)


def generate_translated_po(obj_id):
    generate_translated_po_task.delay(obj_id)


def generate_translated_json(obj_id):
    generate_translated_json_task.delay(obj_id)
