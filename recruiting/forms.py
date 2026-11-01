from django import forms
from django.core.exceptions import ValidationError
from .models import Application, ApplicationDepartment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [super(MultipleFileField, self).clean(item, initial) for item in data]


class ApplicationForm(forms.ModelForm):
    certificates_uploads = MultipleFileField(required=False, label="Zeugnisse und Zertifikate")
    department = forms.ChoiceField(label="Gewünschter Bereich", required=True)

    def __init__(self, *args, vacancy=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.vacancy = vacancy
        self.fields["department"].required = vacancy is None
        self.fields["department"].choices = [("", "Bitte Bereich auswählen")] + [
            (item.name, item.name) for item in ApplicationDepartment.objects.filter(active=True)
        ]
        if vacancy is not None:
            self.fields["department"].initial = vacancy.get_category_display()

    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "department", "available_from", "motivation", "cv", "cover_letter", "certificates_uploads", "privacy_consent"]
        widgets = {"motivation": forms.Textarea(attrs={"rows": 5}), "privacy_consent": forms.CheckboxInput()}
    def clean_department(self):
        if self.vacancy is not None:
            return self.vacancy.get_category_display()
        return self.cleaned_data.get("department")

    def clean_privacy_consent(self):
        if not self.cleaned_data.get("privacy_consent"):
            raise ValidationError("Bitte bestätigen Sie die Datenschutzhinweise")
        return True
    def clean(self):
        data = super().clean()
        for name in ("cv", "cover_letter", "certificates_uploads"):
            files = data.get(name) if name == "certificates_uploads" else [data.get(name)]
            if not files: continue
            if name == "certificates_uploads" and len(files) > 10:
                self.add_error(name, "Maximal 10 Dateien")
            for file in files:
                if not file: continue
                self._validate_upload(name, file)
        return data

    def _validate_upload(self, name, file):
            if file.size > 5 * 1024 * 1024:
                self.add_error(name, "Maximal 5 MB pro Datei")
            ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
            allowed = ("pdf",) if name in ("cv", "cover_letter") else ("pdf", "jpg", "jpeg", "png")
            if ext not in allowed:
                self.add_error(name, "Bitte PDF verwenden" if name != "certificates_uploads" else "PDF, JPG oder PNG verwenden")
            file.seek(0)
            sig = file.read(8); file.seek(0)
            valid = sig.startswith(b"%PDF-") if ext == "pdf" else (sig.startswith(b"\xff\xd8\xff") if ext in ("jpg", "jpeg") else sig.startswith(b"\x89PNG\r\n\x1a\n"))
            if not valid: self.add_error(name, "Ungültiges Dateiformat")
