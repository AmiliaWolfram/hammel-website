# HAMMEL DE – Phase 33: HR Mehrsprachigkeit

Für HR-Tipps und beide Bereichsarten zeigt das deutsche Bearbeitungsformular jetzt Sprachwechsel zu EN/FR/ES/IT. Neue Datensätze werden zuerst auf Deutsch gespeichert und danach automatisch zum Sprachversionseditor weitergeleitet. Übersetzungen werden weiterhin im bestehenden ContentTranslation-Modell gespeichert; vorhandene Übersetzungen bleiben erhalten.

## Sicheres Update

Dieses Archiv enthält KEINE Datenbank. Bestehende Datenbank nicht ersetzen. Projektcode in bestehendes Projekt übernehmen, danach `python manage.py check` ausführen. Es sind keine neuen Migrationen erforderlich.

## Verhalten

- Deutsche Originalfelder bleiben maßgeblich.
- Reihenfolge, Aktiv-/Veröffentlichungsstatus bleiben sprachübergreifend.
- Der Sprachversionseditor verwendet weiterhin die bestehenden Status Entwurf, In Prüfung, Veröffentlicht.
- Bestehende Übersetzungen werden nicht überschrieben.
- Öffentliche Seiten nutzen die bestehende Übersetzungsfunktion; deren vollständige Sprachumschaltung ist nicht Bestandteil dieser Änderung.
