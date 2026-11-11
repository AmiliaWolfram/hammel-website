HAMMEL Sprachversionen – Phase 4

Predefined checkbox entries: HRTextBlock; approved translations: ContentTranslation with status=published.
When saving a vacancy, existing approved library translations are copied into vacancy translation drafts.
Missing/custom lines stay in German and MUST be manually translated before publication.
No external translation service is used. No migration required.
Existing human-edited translations are never overwritten.

To populate drafts for previously saved vacancies:
  python manage.py shell -c "from recruiting.models import Vacancy; from translations.services import fill_vacancy_from_library; [fill_vacancy_from_library(v) for v in Vacancy.objects.all()]"

IMPORTANT: Previously imported vacancy lines may already exist as HRTextBlock entries.
Only approved library translations are reused, and only if source text matches.

Test using python manage.py check and a backup of your database before deployment.
