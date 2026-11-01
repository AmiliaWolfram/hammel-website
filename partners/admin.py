from django.contrib import admin
from .models import Partner
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display=("name","country","region","published","sort_order")
    list_filter=("region","published")
    search_fields=("name","country","city")
