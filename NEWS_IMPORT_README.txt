HAMMEL WAS UNS BEWEGT — editorial starter content

From the project folder run:
  python manage.py migrate
  python manage.py runserver

The migration 0006 seeds three published articles only if their source URL is not already in the database. It does not delete existing news or Messen.

IMPORTANT: Exact original publication dates were not confirmed for these articles. January 1 is a database placeholder used only to store the known year; the frontend intentionally displays only the year for these entries. Edit dates in Django Admin when verified.

Article teaser/body text is newly summarized; full original content remains accessible by link. Illustrations are existing local HAMMEL site assets, not necessarily photos from the corresponding article. Upload correct article photos in Newsverwaltung to override them.

The feature story is 25 JAHRE (R)EVOLUTION!.
