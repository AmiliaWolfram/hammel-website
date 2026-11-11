HAMMEL DE — Phase 37: HR workflow safety

Changes:
- Translation drafts are saved to the current database by AJAX (single field at a time).
- Language switches wait for pending saves; failed saves block navigation.
- Published translation status is never granted by autosave.
- Review shows finished / needs review / missing / stale counts per language.
- German publication requires key fields and an explicit confirmation checkbox.
- Shared editor spacing CSS for Deutsch / Übersetzungen / Prüfung.
- Automated workflow tests are included but MUST be run on your machine.

IMPORTANT: Do NOT replace your current database. No db.sqlite3 is included.
No schema changes and no migrations are needed.

After applying files to your existing project:
    python manage.py check
    python manage.py test recruiting.test_hr_workflow
    python manage.py runserver

Test manually with a test vacancy before using live data:
1. Create a vacancy, enter the German original and save.
2. Type an EN translation, immediately switch to FR, then back to EN.
3. Confirm the EN text was saved; repeat for ES and IT.
4. Check the review counters and the missing-field list.
5. Try publishing with missing German fields and without the confirmation.
6. Complete fields, confirm, publish, then edit and verify the published page.

This package was statically validated; Django runtime/browser tests could not be
executed in the build environment because Django is not installed there.
