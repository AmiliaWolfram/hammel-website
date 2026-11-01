# HAMMEL Karriere / HR

Run `python manage.py migrate` and `python manage.py createsuperuser`.

## Annett permissions
Create a normal Django user for Annett in `/django-intern-admin/`. Do NOT grant `is_staff` to an untrusted account; for Annett, set `is_staff=True`, `is_superuser=False`, and grant only recruiting permissions (`view/add/change/delete vacancy`, `view/change application`, `view/add/change/delete hrtip`). Never share an admin password. The protected HR dashboard is `/staff/karriere/`. Django admin is `/django-intern-admin/recruiting/`.

## Mail
Set `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT`, `DJANGO_EMAIL_USE_TLS`, `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD`, `DJANGO_DEFAULT_FROM_EMAIL`, `HAMMEL_HR_EMAIL`. Default is console backend for development, which prints mail rather than delivering it. Emails contain no CV or sensitive application contents.

## Privacy and deployment
Applications are saved to the database first; email delivery is a secondary notification. Uploaded CVs are sensitive. In production DO NOT expose `/media/hr/` publicly: use private object storage and authenticated downloads, encrypted backups, retention/deletion policy, antivirus scanning, rate limiting, and a legally reviewed privacy notice. Current file storage is suitable only for restricted development/testing. Obtain HR approval before using in production. Confirm vacancy accuracy and publish only current offers.
