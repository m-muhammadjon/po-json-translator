from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from main.forms import PoFileForm
from main.models import File
from main.utils import generate_translated_json, generate_translated_po


def index(request):
    files = File.objects.all().order_by("-created_at")
    form = PoFileForm()
    return render(request, "main/index.html", {"form": form, "files": files})


@require_POST
def translate(request):
    form = PoFileForm(request.POST, request.FILES)
    src = request.POST.get("from_lang")
    dest = request.POST.get("to_lang")
    valid_langs = {
        "uz": ["cry", "kaa", "en", "ru"],
        "cry": ["uz", "kaa"],
        "kaa": ["uz", "cry"],
        "en": ["uz", "ru", "en", "cry", "kaa"],
        "ru": ["uz", "en", "ru"],
    }
    file_type = str(request.FILES.get("file")).split(".")[-1]  # noqa

    if src not in valid_langs or dest not in valid_langs[src]:
        return HttpResponse("Invalid language combination", status=400)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        if obj.type == "po":
            print("po")
            generate_translated_po(obj.id)
        elif obj.type == "json":
            generate_translated_json(obj.id)
        return redirect("main:index")
