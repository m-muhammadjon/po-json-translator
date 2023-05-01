from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from main.forms import FileForm
from main.models import File
from main.tasks import (generate_translated_json_task,
                        generate_translated_po_task)


def index(request) -> HttpResponse:
    files = File.objects.all().order_by("-created_at")
    form = FileForm()
    return render(request, "main/index.html", {"form": form, "files": files})


@require_POST
def translate(request) -> HttpResponse:
    form = FileForm(request.POST, request.FILES)
    src = request.POST.get("from_lang")
    dest = request.POST.get("to_lang")
    valid_langs = {
        "uz": ["cry", "kaa", "en", "ru"],
        "cry": ["uz", "kaa"],
        "kaa": ["uz", "cry"],
        "en": ["uz", "ru", "en", "cry", "kaa"],
        "ru": ["uz", "en", "ru"],
    }
    file_type = str(request.FILES.get("file")).split(".")[-1]

    if src not in valid_langs or dest not in valid_langs[src]:
        return HttpResponse("Invalid language combination", status=400)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.type = file_type
        obj.save()
        if file_type == "po":
            generate_translated_po_task.delay(obj.id)
        elif file_type == "json":
            generate_translated_json_task.delay(obj.id)
        return redirect("main:index")
