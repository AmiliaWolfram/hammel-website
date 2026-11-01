from django import forms
from .models import Messe

class MesseForm(forms.ModelForm):
    class Meta:
        model = Messe
        fields = ("title", "start_date", "end_date", "city", "country", "booth", "description", "url", "image", "published")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 5}),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

from .models import NewsArticle

class NewsArticleForm(forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = ("title", "category", "published_at", "teaser", "body", "image", "featured", "published")
        widgets = {
            "published_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "teaser": forms.Textarea(attrs={"rows": 3}),
            "body": forms.Textarea(attrs={"rows": 12}),
        }


from .models import UsedMachine
class UsedMachineForm(forms.ModelForm):
    class Meta:
        model = UsedMachine
        fields = ("title", "serial_number", "build_year", "build_month", "operating_hours", "engine", "power", "shafts", "condition", "equipment", "weight", "description", "image", "video_url", "position", "published")
        widgets = {"shafts": forms.Textarea(attrs={"rows": 3}), "condition": forms.Textarea(attrs={"rows": 4}), "equipment": forms.Textarea(attrs={"rows": 4}), "description": forms.Textarea(attrs={"rows": 5})}

from .models import MachineProduct, MachineVariant

class MachineProductForm(forms.ModelForm):
    class Meta:
        model = MachineProduct
        fields = ("category","model_name","headline","description","advantages","image","image_url","position","published")
        widgets = {key:forms.Textarea(attrs={"rows":4}) for key in ("description","advantages")}

class MachineVariantForm(forms.ModelForm):
    class Meta:
        model = MachineVariant
        fields = ("product","name","version","description","operating_principle","engine","drive","weight","additional_specs","image","image_url","hero_media_choice","hero_video","hero_video_url","datasheet_url","technical_drawing","technical_drawing_url","position","published")
        widgets = {key:forms.Textarea(attrs={"rows":4}) for key in ("description","operating_principle","additional_specs")}


# These controls are handled explicitly in the Vertrieb form to keep area/material
# selection structured, rather than a free-text comma-separated field.
