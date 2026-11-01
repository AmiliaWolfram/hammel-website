from django import forms
from .models import Partner
class PartnerForm(forms.ModelForm):
    class Meta:
        model=Partner
        fields=["name","country","city","address","phone","email","domain","description","eyebrow","specialties","source_url","theme","tagline","brand_color","hero_image","official_logo","region","latitude","longitude","logo","logo_url","sort_order","published"]
        widgets={"address":forms.Textarea(attrs={"rows":2}),"description":forms.Textarea(attrs={"rows":4})}
    def clean_specialties(self):
        value=self.cleaned_data.get("specialties")
        if not isinstance(value,list) or any(not isinstance(x,str) for x in value):
            raise forms.ValidationError("Bitte eine JSON-Liste mit Texten eingeben.")
        return value
    def clean_logo(self):
        logo=self.cleaned_data.get("logo")
        if logo and hasattr(logo,"size") and logo.size>3*1024*1024:raise forms.ValidationError("Logo darf maximal 3 MB groß sein.")
        if logo and hasattr(logo,"content_type") and logo.content_type not in ("image/png","image/jpeg","image/webp","image/gif"):raise forms.ValidationError("Bitte PNG, JPG, WebP oder GIF verwenden.")
        return logo
