"""Staff views for managing contact groups and contact people."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactGroupForm, ContactPersonForm
from .models import ContactGroup, ContactPerson


CONTACT_TYPES = {
    "person": (ContactPerson, ContactPersonForm),
    "gruppe": (ContactGroup, ContactGroupForm),
}


def require_model_permission(request, kind, action):
    """Return the model and form only when the user has the required permission."""
    if kind not in CONTACT_TYPES:
        raise PermissionDenied

    model, form_class = CONTACT_TYPES[kind]
    permission = f"contacts.{action}_{model._meta.model_name}"
    if not request.user.has_perm(permission):
        raise PermissionDenied

    return model, form_class


@login_required(login_url="messen_login")
def dashboard(request):
    can_view_people = request.user.has_perm("contacts.view_contactperson")
    can_view_groups = request.user.has_perm("contacts.view_contactgroup")
    if not (can_view_people or can_view_groups):
        raise PermissionDenied

    context = {
        "people": ContactPerson.objects.select_related("group").all(),
        "groups": ContactGroup.objects.all(),
        "website_groups": ContactGroup.objects.prefetch_related("people").all(),
    }
    return render(request, "contacts/dashboard.html", context)


@login_required(login_url="messen_login")
def edit(request, kind, pk=None):
    action = "change" if pk is not None else "add"
    model, form_class = require_model_permission(request, kind, action)
    instance = get_object_or_404(model, pk=pk) if pk is not None else None
    form = form_class(request.POST or None, instance=instance)

    if request.method == "POST" and form.is_valid():
        saved = form.save()
        from translations.services import save_inline

        save_inline(request, saved, form)
        messages.success(request, "Änderungen wurden gespeichert.")
        return redirect("contacts_dashboard")

    context = {
        "form": form,
        "editing": bool(instance),
        "kind": kind,
        "object": instance,
    }
    return render(request, "contacts/form.html", context)


@login_required(login_url="messen_login")
def delete(request, kind, pk):
    model, _ = require_model_permission(request, kind, "delete")
    instance = get_object_or_404(model, pk=pk)

    if request.method == "POST":
        try:
            instance.delete()
        except Exception:
            messages.error(
                request,
                "Diese Gruppe enthält noch Kontakte. "
                "Bitte zuerst Kontakte verschieben oder löschen.",
            )
        else:
            messages.success(request, "Eintrag wurde gelöscht.")
        return redirect("contacts_dashboard")

    return render(request, "contacts/delete.html", {"item": instance})


@login_required(login_url="messen_login")
@require_POST
def reorder(request, kind):
    """Persist an exact drag-and-drop order without changing other contact data."""
    model, _ = require_model_permission(request, kind, "change")
    try:
        payload = json.loads(request.body)
        ids = payload["ids"]
        if (
            not isinstance(ids, list)
            or any(type(pk) is not int or pk <= 0 for pk in ids)
            or len(ids) != len(set(ids))
        ):
            raise ValueError
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Ungültige Reihenfolge."}, status=400)

    with transaction.atomic():
        existing = list(model.objects.select_for_update().values_list("pk", flat=True))
        if len(ids) != len(existing) or set(ids) != set(existing):
            return JsonResponse(
                {"error": "Liste wurde geändert. Bitte neu laden."}, status=409
            )
        model.objects.bulk_update(
            [model(pk=pk, sort_order=position) for position, pk in enumerate(ids, 1)],
            ["sort_order"],
        )
    return JsonResponse({"ok": True})


@login_required(login_url="messen_login")
@require_POST
def reorder_group_people(request, group_id):
    """Order contacts inside one group only, preserving every other group."""
    require_model_permission(request, "person", "change")
    group = get_object_or_404(ContactGroup, pk=group_id)
    try:
        ids = json.loads(request.body)["ids"]
        if not isinstance(ids, list) or any(type(pk) is not int or pk <= 0 for pk in ids) or len(ids) != len(set(ids)):
            raise ValueError
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Ungültige Reihenfolge."}, status=400)
    with transaction.atomic():
        existing = set(ContactPerson.objects.select_for_update().filter(group=group).values_list("pk", flat=True))
        if set(ids) != existing or len(ids) != len(existing):
            return JsonResponse({"error": "Liste wurde geändert. Bitte neu laden."}, status=409)
        ContactPerson.objects.bulk_update(
            [ContactPerson(pk=pk, sort_order=i) for i, pk in enumerate(ids, 1)],
            ["sort_order"],
        )
    return JsonResponse({"ok": True})
