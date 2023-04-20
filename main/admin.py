from django.contrib import admin

from main.models import File


@admin.register(File)
class PoFileAdmin(admin.ModelAdmin):
    list_display = ("id", "from_lang", "to_lang", "execution_time", "created_at", "result_file")
    list_filter = ("from_lang", "to_lang", "created_at")
    search_fields = ("file",)
    ordering = ("-created_at",)
