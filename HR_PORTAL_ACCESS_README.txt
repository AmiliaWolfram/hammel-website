HR-Portal Zugangsschutz
========================
Login: /staff/karriere/login/
Logout: /staff/karriere/logout/ (POST mit CSRF)
Dashboard: /staff/karriere/

Alle HR-Seiten erfordern Login und das Django-Recht recruiting.view_application.
Schreibzugriff benötigt zusätzlich die jeweiligen add/change/delete Rechte.

Zugänge im Django-Admin (/django-intern-admin/) anlegen: Benutzer anlegen,
aktivieren und Berechtigung recruiting | application | Can view application vergeben.
Für redaktionelle Rollen die jeweiligen Modellrechte vergeben.
Alternativ eine Gruppe HR-Team mit diesen Rechten erstellen und Benutzer zuordnen.
Keine Passwörter im Code hinterlegen.

Wichtig: Django-Superuser haben grundsätzlich alle Rechte. Für Produktivbetrieb
HTTPS, sichere Session-Cookies und begrenzte Admin-Rechte verwenden.
