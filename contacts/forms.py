from django import forms
from .models import ContactGroup, ContactPerson

class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = ContactPerson
        fields = ["name", "group", "role", "region", "phone", "email", "sort_order", "published"]
        widgets = {"region": forms.Textarea(attrs={"rows": 3}), "phone": forms.Textarea(attrs={"rows": 3})}

class ContactGroupForm(forms.ModelForm):
    class Meta:
        model = ContactGroup
        fields = ["name", "sort_order", "published"]
