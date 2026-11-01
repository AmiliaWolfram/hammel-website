from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from .models import ContactGroup, ContactPerson
from .forms import ContactGroupForm, ContactPersonForm

@login_required(login_url="messen_login")
def dashboard(request):
    if not (request.user.has_perm("contacts.view_contactperson") or request.user.has_perm("contacts.view_contactgroup")):
        raise PermissionDenied
    return render(request, "contacts/dashboard.html", {"people": ContactPerson.objects.select_related("group").all(), "groups": ContactGroup.objects.all()})

MODELS = {"person": (ContactPerson, ContactPersonForm), "gruppe": (ContactGroup, ContactGroupForm)}

def require_model_permission(request, kind, action):
    if kind not in MODELS:
        raise PermissionDenied
    model, form_class = MODELS[kind]
    if not request.user.has_perm(f"contacts.{action}_{model._meta.model_name}"):
        raise PermissionDenied
    return model, form_class

@login_required(login_url="messen_login")
def edit(request, kind, pk=None):
    model, form_class = require_model_permission(request, kind, "change" if pk is not None else "add")
    instance = get_object_or_404(model, pk=pk) if pk is not None else None
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Änderungen wurden gespeichert.")
        return redirect("contacts_dashboard")
    return render(request, "contacts/form.html", {"form": form, "editing": bool(instance), "kind": kind})

@login_required(login_url="messen_login")
def delete(request, kind, pk):
    model, _ = require_model_permission(request, kind, "delete")
    instance = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        try:
            instance.delete()
        except Exception:
            messages.error(request, "Diese Gruppe enthält noch Kontakte. Bitte zuerst Kontakte verschieben oder löschen.")
        else:
            messages.success(request, "Eintrag wurde gelöscht.")
        return redirect("contacts_dashboard")
    return render(request, "contacts/delete.html", {"item": instance})
