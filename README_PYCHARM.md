# HAMMEL — Complete Django website for PyCharm

This archive contains the **entire 9-page HAMMEL website** and one integrated Django application for publishing Messen. No separate HTML server is needed.

## 1. Open in PyCharm

1. Unzip the archive and open **HAMMEL_Django** as the project folder.
2. Configure a Python 3.11+ virtual environment (Settings > Project > Python Interpreter).
3. In PyCharm Terminal:

   ```bash
   python -m pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

4. Open http://127.0.0.1:8000/ for HOME and http://127.0.0.1:8000/aktuelles/index.html for MESSEN.
5. Staff login: http://127.0.0.1:8000/staff/messen/

## 2. Publish exhibitions

Sign in as superuser. Under **Messen**, click **Hinzufügen** and enter title, start/end dates, city, country, stand, description, optional image and URL. Check **Öffentlich sichtbar** and save. The event immediately appears on the public page; unpublished entries are invisible to visitors.

To add employees: Admin > Benutzer > Hinzufügen; enable **Mitarbeiter-Status** (is_staff) and grant only **Messen | Messe** view/add/change/delete permissions. **Do not grant superuser access** to ordinary employees. Staff must log in; the admin is not publicly editable.

## 3. Project structure

- `website/` — all 9 existing HTML pages, assets, videos, images, styles and JS.
- `config/` — Django settings, URL routes and WSGI.
- `messen/` — database model, staff admin, migrations, published-only JSON API.
- `templates/admin/base_site.html` — HAMMEL branding for Django administration.
- `website/assets/css/hammel-admin.css` — staff admin theme.

The public HTML is served by Django at the same `/.../index.html` URLs, preserving existing relative links. Static files are served at `/assets/`. Staff edits are stored in `db.sqlite3` in development; uploaded images are stored in `media/`.

## 4. Production deployment (important)

- Set `DJANGO_DEBUG=0`, a strong `DJANGO_SECRET_KEY`, and correct `DJANGO_ALLOWED_HOSTS`.
- Run `python manage.py collectstatic --noinput` (WhiteNoise serves static assets).
- Use HTTPS, an appropriate WSGI server and persistent database/storage; configure hosting to serve `/media/` images securely.
- Do not publish `db.sqlite3`, `.env`, or `media/` in Git. Use backups and strong staff passwords; MFA recommended.
- Review image rights and public content before launch.
- The admin is **not secured merely by an obscure URL**; Django session authentication, CSRF and per-model permissions protect writes.
- Django isn't bundled as a Python package; install dependencies from `requirements.txt`.

## 5. Notes

No exhibition entries have been invented. The MESSEN page shows a neutral empty state until an employee publishes an event. The supplied four category videos and all other site content remain in the project.


## Neue HAMMEL Messenverwaltung (eigene Oberfläche)
- `/staff/messen/` – nur Messe-Übersicht, mit Hinzufügen/Bearbeiten/Löschen.
- `/staff/messen/login/` – Mitarbeiter-Login.
- `/django-intern-admin/` – Django-Systemverwaltung für Superuser (Benutzer- und Rechtevergabe), nicht in der Messen-Oberfläche verlinkt.
- Für Mitarbeiter: `is_staff` ist für das neue Dashboard nicht zwingend nötig, aber `messen.view_messe` und je nach Rolle `add_messe`, `change_messe`, `delete_messe` sind erforderlich. In Django Admin Benutzer/Gruppen zuweisen. Superuser haben alle Rechte.
- Bilder werden nach `media/messen/` gespeichert; im Produktivbetrieb muss `/media/` sicher durch den Webserver bereitgestellt werden.
- Die öffentliche API `/api/messen/` liefert weiterhin ausschließlich veröffentlichte Veranstaltungen.
