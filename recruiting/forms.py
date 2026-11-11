from django import forms
import io
import zipfile
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
        if vacancy is not None:
            # A job application does not render the department selector.
            # Never validate a hidden field against unrelated initiative choices.
            self.fields["department"].choices = [("", "Automatisch aus der Stelle übernommen")]
            self.fields["department"].initial = ""
        else:
            self.fields["department"].choices = [("", "Bitte Bereich auswählen")] + [
                (item.name, item.name) for item in ApplicationDepartment.objects.filter(active=True)
            ]

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
        if file.size > 10 * 1024 * 1024:
            self.add_error(name, "Maximal 10 MB pro Datei")
            return
        ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
        allowed = ("pdf", "doc", "docx") if name in ("cv", "cover_letter") else ("pdf", "jpg", "jpeg", "png")
        if ext not in allowed:
            self.add_error(name, "Erlaubte Formate: " + ", ".join(x.upper() for x in allowed))
            return
        file.seek(0)
        signature = file.read(8)
        file.seek(0)
        if ext == "pdf":
            valid = signature.startswith(b"%PDF-")
        elif ext == "doc":
            valid = signature.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))
        elif ext == "docx":
            valid = False
            if signature.startswith(b"PK"):
                try:
                    with zipfile.ZipFile(file) as document:
                        valid = "word/document.xml" in document.namelist() and "[Content_Types].xml" in document.namelist()
                except (zipfile.BadZipFile, OSError, ValueError):
                    valid = False
        elif ext in ("jpg", "jpeg"):
            valid = signature.startswith(bytes.fromhex("FFD8FF"))
        else:
            valid = signature.startswith(bytes.fromhex("89504E470D0A1A0A"))
        file.seek(0)
        if not valid:
            self.add_error(name, "Die Datei entspricht nicht dem angegebenen Dateiformat")
