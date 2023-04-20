from django.core.validators import FileExtensionValidator
from django.db import models


class LanguageChoices(models.TextChoices):
    en = ("en", "English")
    ru = ("ru", "Russian")
    uz = ("uz", "Uzbek")
    cry = ("cry", "Cyrillic")
    kaa = ("kaa", "Karakalpak")


class File(models.Model):
    file = models.FileField(
        upload_to="files",
        validators=[FileExtensionValidator(allowed_extensions=["po", "json"])],
    )
    attempts = models.IntegerField(default=0)
    status = models.CharField(max_length=255, default="Pending")
    result_file = models.URLField(null=True, blank=True)
    from_lang = models.CharField(max_length=10, choices=LanguageChoices.choices)
    to_lang = models.CharField(max_length=10, choices=LanguageChoices.choices)
    user = models.ForeignKey("auth.User", models.SET_NULL, null=True)
    execution_time = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
