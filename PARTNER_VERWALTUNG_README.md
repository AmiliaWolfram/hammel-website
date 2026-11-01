# Partnerverwaltung

`python manage.py migrate` imports the 45 existing partners from WELTWEIT into the database. Existing records are not overwritten.

Grant staff users the `partners.view_partner`, `add_partner`, `change_partner`, `delete_partner` permissions in Django Admin. The tile then appears in VERTRIEBSPORTAL.

Logos uploaded via the form are served from MEDIA_URL in DEBUG. In production, configure secure media storage and web-server media serving. Existing public logo URLs are retained as fallback on WELTWEIT when no uploaded logo is available.

The public map loads `/api/partner/` and displays only published records. The legacy static array is retained only as a fallback for offline previews. Latitude and longitude should be set for new partners.
