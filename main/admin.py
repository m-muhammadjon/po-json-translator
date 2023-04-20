from django.contrib import admin

from main.models import File


@admin.register(File)
class PoFileAdmin(admin.ModelAdmin):
    list_display = ("id", "from_lang", "to_lang", "user", "execution_time", "created_at", "result_file")
    list_filter = ("from_lang", "to_lang", "user", "created_at")
    search_fields = ("file", "user__username")
    ordering = ("-created_at",)
