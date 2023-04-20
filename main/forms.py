from django import forms

from main.models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ("file", "from_lang", "to_lang")
