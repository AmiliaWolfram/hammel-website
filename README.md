# HAMMEL Messen — secure staff administration

The public website is static HTML/CSS/JS. **A hidden HTML page is not access control.**
This Django starter provides a database, authenticated staff-only admin, and public JSON API.

## Setup
1. Install Python 3.11+ and run `pip install -r requirements.txt`.
2. Set `DJANGO_SECRET_KEY` (a strong secret), `DJANGO_ALLOWED_HOSTS` (comma-separated domains),
   `DJANGO_CSRF_TRUSTED_ORIGINS` (https://your-domain), and `DJANGO_DEBUG=0`.
3. Run `python manage.py migrate`.
4. Run `python manage.py createsuperuser` and log in at `/staff/messen/`.
5. Assign `is_staff=True` and specific Messen permissions to trusted employees.
6. Serve the backend on the same origin as the public website, proxy `/api/messen/` and
   `/staff/messen/` to Django, and serve the website static files separately.

## Security
- Admin requires authenticated staff with appropriate model permissions.
- Unpublished entries are never returned by `/api/messen/`.
- CSRF protection, Django session security, secure cookies (HTTPS), and clickjacking protection enabled.
- Use HTTPS, production database/backups, strong passwords and ideally MFA via a compatible plugin.
- Change the secret and domain environment variables before deployment.
- Static preview JSON (`assets/data/messen.json`) is intentionally empty; do not place unpublished
  information there. The API must be hosted to make employee edits appear on the website.
- The example is **not deployed**; staff editing won't work until the server is configured.
