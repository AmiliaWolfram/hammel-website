from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import ContactGroup

@require_GET
def published_contacts(request):
    groups = ContactGroup.objects.filter(published=True).prefetch_related("people")
    return JsonResponse({"groups": [{"id":g.id,"name":g.name,"contacts":[{
        "name":p.name,"role":p.role,"region":p.region,
        "phones":[x.strip() for x in p.phone.splitlines() if x.strip()],"email":p.email
    } for p in g.people.all() if p.published]} for g in groups]})
