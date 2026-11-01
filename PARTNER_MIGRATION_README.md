# Partnerdaten vollständig in Django

`python manage.py migrate` ausführen. Migration 0003 übernimmt vorhandene redaktionelle Texte, Schwerpunkte, Claims, Farben, Bild- und Logo-URLs aus der bisherigen JavaScript-Datei. Bereits ausgefüllte Datenbankfelder werden nicht überschrieben. Die WELTWEIT-Karte liest ihre Partner ausschließlich aus `/api/partner/`.

Bei neuen Partnern können die Schwerpunkte im Formular als JSON-Liste eingegeben werden, z. B. `["Recycling", "Service"]`. Externe Logos bleiben URLs, bis sie manuell hochgeladen werden. Das bisherige statische JS-Datenmodul bleibt als Archivdatei vorhanden, wird aber nicht mehr eingebunden.
