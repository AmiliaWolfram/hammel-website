from django.contrib import admin
from .models import ContactGroup, ContactPerson

@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "published")
    list_editable = ("sort_order", "published")
    search_fields = ("name",)

@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "role", "email", "published", "sort_order")
    list_filter = ("group", "published")
    search_fields = ("name", "role", "email", "region", "phone")
    list_editable = ("published", "sort_order")
    ordering = ("sort_order", "name")
