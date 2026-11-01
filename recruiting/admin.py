from django.contrib import admin
from .models import Vacancy, Application, HRTip, ApplicationDepartment, ApplicationCertificate

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "location", "published", "updated_at")
    list_filter = ("published", "category")
    search_fields = ("title", "introduction")
    list_editable = ("published",)

class ApplicationCertificateInline(admin.TabularInline):
    model = ApplicationCertificate
    extra = 0
    readonly_fields = ("file", "uploaded_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    inlines = (ApplicationCertificateInline,)
    list_display = ("full_name", "vacancy", "created_at", "status", "notification_sent")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email")
    readonly_fields = ("vacancy", "full_name", "email", "phone", "department", "available_from", "motivation", "cv", "cover_letter", "certificates", "privacy_consent", "created_at", "notification_sent")
    def has_add_permission(self, request): return False

@admin.register(HRTip)
class HRTipAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "order")
    list_editable = ("published", "order")


@admin.register(ApplicationDepartment)
class ApplicationDepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "sort_order")
    list_editable = ("active", "sort_order")
    list_filter = ("active",)
    search_fields = ("name",)
    ordering = ("sort_order", "name")
