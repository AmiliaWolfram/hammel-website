"""Public website pages + staff-only Django admin + published events API."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from messen.views import machine_catalog, machine_product_detail, machine_variant_detail, machine_series_compare, published_messen, published_news, website_page, news_story, used_machines, used_machine_detail
from messen import staff_views
from recruiting import views as hr_views
from contacts.views import published_contacts
from contacts import staff_views as contact_staff
from partners import views as partner_views

admin.site.site_header = "HAMMEL · Vertriebsportal"
admin.site.site_title = "HAMMEL Messen"
admin.site.index_title = "Veranstaltungen verwalten"

urlpatterns = [
    path("api/loesungen/maschinen/", __import__("messen.views", fromlist=["recycling_machines_overview"]).recycling_machines_overview, name="recycling_machines_overview"),
    path("api/partner/", partner_views.published, name="published_partners"),
    path("staff/partner/", partner_views.dashboard, name="partners_dashboard"),
    path("staff/partner/neu/", partner_views.edit, name="partners_create"),
    path("staff/partner/<int:pk>/bearbeiten/", partner_views.edit, name="partners_edit"),
    path("staff/partner/<int:pk>/loeschen/", partner_views.delete, name="partners_delete"),
    path("api/ansprechpartner/", published_contacts, name="published_contacts"),
    path("staff/kontakte/", contact_staff.dashboard, name="contacts_dashboard"),
    path("staff/kontakte/<str:kind>/neu/", contact_staff.edit, name="contacts_create"),
    path("staff/kontakte/<str:kind>/<int:pk>/bearbeiten/", contact_staff.edit, name="contacts_edit"),
    path("staff/kontakte/<str:kind>/<int:pk>/loeschen/", contact_staff.delete, name="contacts_delete"),
    # Transport is not a HAMMEL service; redirect outdated bookmarks.
    path("service/transport/", RedirectView.as_view(url="/service/index.html", permanent=False)),
    path("service/transport/index.html", RedirectView.as_view(url="/service/index.html", permanent=False)),
    path("maschinen/", machine_catalog, name="machine_catalog"),
    path("maschinen/index.html", machine_catalog),
    path("maschinen/modell/<int:pk>/", machine_product_detail, name="machine_product_detail"),
    path("maschinen/variante/<int:pk>/", machine_variant_detail, name="machine_variant_detail"),
    path("maschinen/modell/<int:pk>/vergleich/", machine_series_compare, name="machine_series_compare"),
    # Messen is a standalone public page, not a redirect to Aktuelles.
    path("messen/", website_page, {"page": "aktuelles"}, name="messen_public"),
    path("messen/index.html", website_page, {"page": "aktuelles"}),
    path("karriere/", hr_views.careers, name="hr_careers"),
    path("karriere/index.html", hr_views.careers),
    path("karriere/initiative/", hr_views.apply, name="hr_initiative"),
    path("karriere/stelle/<slug:slug>/", hr_views.job_detail, name="hr_job_detail"),
    path("karriere/stelle/<slug:slug>/bewerben/", hr_views.apply, name="hr_apply_job"),
    path("karriere/hr-tipps/", hr_views.tips, name="hr_tips"),
    path("staff/karriere/login/", hr_views.HRLoginView.as_view(), name="hr_login"),
    path("staff/karriere/logout/", hr_views.HRLogoutView.as_view(), name="hr_logout"),
    path("staff/karriere/", hr_views.hr_dashboard, name="hr_dashboard"),
    path("staff/karriere/verwaltung/", hr_views.hr_management, name="hr_management"),
    path("staff/karriere/verwaltung/<slug:section>/", hr_views.hr_section, name="hr_section"),
    path("staff/karriere/<str:kind>/neu/", hr_views.hr_edit, name="hr_new"),
    path("staff/karriere/<str:kind>/<int:pk>/", hr_views.hr_edit, name="hr_edit"),
    path("staff/karriere/<str:kind>/<int:pk>/loeschen/", hr_views.hr_delete, name="hr_delete"),
    path("", website_page, {"page": ""}, name="home"),
    path("index.html", website_page, {"page": ""}),
    path("staff/", staff_views.staff_home, name="staff_home"),
    path("api/loesungen/<slug:slug>/maschinen/", __import__("messen.views", fromlist=["recycling_area_machines"]).recycling_area_machines, name="recycling_area_machines"),
    path("staff/maschinen/felder/", staff_views.machine_fields_manage, name="staff_machine_fields_manage"),
    path("staff/maschinen/varianten/<int:pk>/felder/", staff_views.machine_custom_values, name="staff_machine_custom_values"),
    path("staff/maschinen/", staff_views.machine_dashboard, name="staff_machine_dashboard"),
    path("staff/maschinen/showcase/", staff_views.showcase_dashboard, name="showcase_dashboard"),
    path("staff/maschinen/showcase/<int:pk>/", staff_views.showcase_edit, name="showcase_edit"),
    path("staff/maschinen/modelle/neu/", staff_views.machine_product_create, name="staff_machine_product_create"),
    path("staff/maschinen/modelle/<int:pk>/", staff_views.machine_product_edit, name="staff_machine_product_edit"),
    path("staff/maschinen/varianten/<int:pk>/kopieren/", staff_views.machine_variant_copy, name="staff_machine_variant_copy"),
    path("staff/maschinen/varianten/neu/", staff_views.machine_variant_create, name="staff_machine_variant_create"),
    path("staff/maschinen/varianten/<int:pk>/", staff_views.machine_variant_edit, name="staff_machine_variant_edit"),
    path("staff/gebrauchtmaschinen/", staff_views.used_dashboard, name="used_dashboard"),
    path("staff/gebrauchtmaschinen/neu/", staff_views.used_create, name="used_create"),
    path("staff/gebrauchtmaschinen/<int:pk>/bearbeiten/", staff_views.used_edit, name="used_edit"),
    path("staff/gebrauchtmaschinen/<int:pk>/loeschen/", staff_views.used_delete, name="used_delete"),
    path("api/gebrauchtmaschinen/", used_machines, name="used_machines"),
    path("service/gebrauchtmaschinen/maschine/<int:pk>/", used_machine_detail, name="used_machine_detail"),
    path("staff/news/", staff_views.news_dashboard, name="news_dashboard"),
    path("staff/news/neu/", staff_views.news_create, name="news_create"),
    path("staff/news/<int:pk>/bearbeiten/", staff_views.news_edit, name="news_edit"),
    path("staff/news/<int:pk>/loeschen/", staff_views.news_delete, name="news_delete"),
    path("staff/messen/", staff_views.dashboard, name="messen_dashboard"),
    path("staff/messen/login/", staff_views.StaffLoginView.as_view(), name="messen_login"),
    path("staff/messen/logout/", staff_views.StaffLogoutView.as_view(), name="messen_logout"),
    path("staff/messen/neu/", staff_views.create, name="messen_create"),
    path("staff/messen/<int:pk>/bearbeiten/", staff_views.edit, name="messen_edit"),
    path("staff/messen/<int:pk>/loeschen/", staff_views.delete, name="messen_delete"),
    path("django-intern-admin/", admin.site.urls),
    path("api/messen/", published_messen, name="published_messen"),
    path("api/news/", published_news, name="published_news"),
    path("was-uns-bewegt/story/<int:pk>/<slug:slug>/", news_story, name="news_story"),
    path("was-uns-bewegt/story/<int:pk>/<slug:slug>/", news_story, name="news_story"),
]
for service_section in ("gebrauchtmaschinen", "mietpark", "transport"):
    urlpatterns.append(path(f"service/{service_section}/index.html", website_page, {"page": f"service/{service_section}"}))
    urlpatterns.append(path(f"service/{service_section}/", RedirectView.as_view(url=f"/service/{service_section}/index.html", permanent=False)))
for section in ("agb", "aeb", "impressum", "datenschutz", "unternehmen", "loesungen", "weltweit", "service", "kontakt", "aktuelles", "was-uns-bewegt"):
    urlpatterns.append(path(f"{section}/index.html", website_page, {"page": section}))
    urlpatterns.append(path(f"{section}/", RedirectView.as_view(url=f"/{section}/index.html", permanent=False)))
# HR uploads are personal data. Do not expose MEDIA_ROOT through public static routes.
# Use authenticated private file delivery in production.

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
