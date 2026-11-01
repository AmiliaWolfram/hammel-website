# Maschinenkatalog und Vertrieb

- `/maschinen/`: DB-basierter Katalog mit Kategorien und Gebrauchtmaschinen.
- `/maschinen/modell/<id>/`: Datenblattseite des Modells.
- `/django-intern-admin/messen/machineproduct/`: Maschinenmodelle hinzufügen/bearbeiten.
- `/staff/gebrauchtmaschinen/`: vorhandene Gebrauchtmaschinenverwaltung.
- `/django-intern-admin/messen/usedmachine/`: Gebrauchtmaschinen über Django-Admin.
- Nach `python manage.py migrate` werden 5 Vorbrecher-Modelle und 7 gebrauchte Maschinen aus der bisherigen HAMMEL-Webseite in die Datenbank übernommen. Existierende Gebrauchtmaschinen mit derselben Seriennummer werden nicht überschrieben.
- Die Gruppe **Vertrieb** wird mit Berechtigungen für Maschinenmodelle und Gebrauchtmaschinen angelegt. Den gewünschten Benutzern diese Gruppe unter `/django-intern-admin/auth/user/` zuweisen; sie brauchen außerdem `is_staff=True`, um den Django-Admin zu benutzen.
- Die Kategorien Nachzerkleinerer, Siebtechnik, Sortiertechnik und Anlagenbau sind vorbereitet, jedoch nicht mit erfundenen Modellen gefüllt. Ein Mitarbeiter kann sie nach Prüfung ergänzen.
- Bilder müssen über Admin hochgeladen werden. Vor Veröffentlichung bitte Gebrauchtmaschinen-Verfügbarkeit und Daten prüfen. Die Importdaten stammen aus dem öffentlichen Altauftritt und sind eine Momentaufnahme.
- Änderungen an den Datensätzen erscheinen ohne erneutes Bearbeiten der HTML-Dateien.
