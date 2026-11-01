from django.contrib import admin
from .models import Messe

@admin.register(Messe)
class MesseAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "city", "booth", "published")
    list_filter = ("published", "start_date", "country")
    search_fields = ("title", "city", "country", "booth")
    list_editable = ("published",)
    ordering = ("-start_date",)
    fieldsets = (
        ("Veranstaltung", {"fields": ("title", "start_date", "end_date", "city", "country")}),
        ("Informationen", {"fields": ("booth", "description", "url", "image")}),
        ("Veröffentlichung", {"fields": ("published",)}),
    )


from .models import MessePhoto
class MessePhotoInline(admin.TabularInline):
    model = MessePhoto
    extra = 0

MesseAdmin.inlines = [MessePhotoInline]


from .models import NewsArticle
@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_at", "featured", "published")
    list_filter = ("category", "published", "featured", "published_at")
    list_editable = ("featured", "published")
    search_fields = ("title", "teaser", "body")
    fieldsets = (("Beitrag", {"fields": ("title", "category", "published_at", "teaser", "body")}), ("Medien & Link", {"fields": ("image", "external_url")}), ("Veröffentlichung", {"fields": ("featured", "published")}))


from .models import UsedMachine, UsedMachinePhoto
class UsedMachinePhotoInline(admin.TabularInline):
    model = UsedMachinePhoto
    extra = 0
@admin.register(UsedMachine)
class UsedMachineAdmin(admin.ModelAdmin):
    list_display = ("title", "serial_number", "build_year", "published", "position")
    list_filter = ("published", "build_year")
    search_fields = ("title", "serial_number")
    inlines = [UsedMachinePhotoInline]


from .models import MachineProduct, MachineVariant
class MachineVariantInline(admin.TabularInline):
    model = MachineVariant
    extra = 0
    fields = ("name", "version", "engine", "drive", "weight", "published", "position")

@admin.register(MachineVariant)
class MachineVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "version", "published", "position")
    list_filter = ("product", "published")
    search_fields = ("name", "engine", "drive")
    list_editable = ("published", "position")
    fieldsets = (("Modell", {"fields": ("product", "name", "version", "description")}),
      ("Einsatzgebiete", {"fields": ("applications_wood", "applications_waste", "applications_other")}),
      ("Technik", {"fields": ("engine", "drive", "weight", "operating_principle", "additional_specs")}),
      ("Medien", {"fields": ("image", "image_url", "hero_video", "hero_video_url", "datasheet_url")}),
      ("Veröffentlichung", {"fields": ("published", "position")}))

@admin.register(MachineProduct)
class MachineProductAdmin(admin.ModelAdmin):
    inlines = [MachineVariantInline]
    list_display = ("model_name", "category", "published", "position", "updated_at")
    list_filter = ("category", "published")
    list_editable = ("published", "position")
    search_fields = ("model_name", "headline", "description", "applications")
    fieldsets = (("Maschine", {"fields": ("category", "model_name", "headline", "description")}),
                 ("Technik", {"fields": ("applications", "technical_data", "advantages")}),
                 ("Medien", {"fields": ("image", "image_url", "datasheet_url")}),
                 ("Veröffentlichung", {"fields": ("published", "position")}))

from .models import RecyclingArea, RecyclingMaterial
@admin.register(RecyclingArea)
class RecyclingAreaAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "position")
@admin.register(RecyclingMaterial)
class RecyclingMaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "area", "position")
    list_filter = ("area",)
    search_fields = ("name",)
