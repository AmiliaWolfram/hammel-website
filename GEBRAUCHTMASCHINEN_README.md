# HAMMEL Gebrauchtmaschinen

1. `python manage.py migrate`
2. Grant the responsible Vertrieb group Django permissions `view_usedmachine`, `add_usedmachine`, `change_usedmachine`, `delete_usedmachine` (and access to `/staff/`). Do not grant permissions to public users.
3. Visit `/staff/gebrauchtmaschinen/` to review seven draft records seeded from the public HAMMEL listing. They are deliberately **unpublished** until images, specifications and availability have been checked.
4. Upload images and set `Auf Website sichtbar` for confirmed machines. Gallery supports multiple uploads.
5. Public page: `/service/gebrauchtmaschinen/`, API: `/api/gebrauchtmaschinen/`, detail: `/service/gebrauchtmaschinen/maschine/<id>/`.
6. YouTube CTA in the hero links to a verified HAMMELBASA video `https://www.youtube.com/watch?v=iVMsYaU4leI`. Replace it with the exact official channel URL if preferred.
7. Existing database is not overwritten; migrations create new tables and draft seed entries only. Uploaded media needs persistent storage in production.
