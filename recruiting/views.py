import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from .forms import ApplicationForm
from .models import Vacancy, Application, ApplicationCertificate, HRTip, ApplicationDepartment

log = logging.getLogger(__name__)

def careers(request):
    # One unified list prevents duplicate AUSBILDUNG headings when some
    # training positions are published and others remain unpublished.
    vacancies = Vacancy.objects.filter(published=True) | Vacancy.objects.filter(published=False, category="ausbildung")
    vacancies = vacancies.order_by("category", "sort_order", "id")
    return render(request, "recruiting/careers.html", {"vacancies": vacancies, "tips": HRTip.objects.filter(published=True)[:3]})

def job_detail(request, slug):
    vacancy = get_object_or_404(Vacancy, slug=slug, published=True)
    return render(request, "recruiting/job.html", {"job": vacancy})

def tips(request):
    return render(request, "recruiting/tips.html", {"tips": HRTip.objects.filter(published=True)})

@require_http_methods(["GET", "POST"])
def apply(request, slug=None):
    vacancy = get_object_or_404(Vacancy, Q(published=True) | Q(category="ausbildung"), slug=slug) if slug else None
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, vacancy=vacancy)
        # A hidden honeypot rejects basic automated submissions.
        if request.POST.get("website", "").strip():
            return render(request, "recruiting/apply.html", {"form": ApplicationForm(vacancy=vacancy), "job": vacancy, "success": True})
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.save()
            for uploaded in form.cleaned_data.get("certificates_uploads", []):
                ApplicationCertificate.objects.create(application=application, file=uploaded)
            try:
                send_mail(
                    f"Neue HAMMEL Bewerbung: {vacancy.title if vacancy else 'Initiativbewerbung'}",
                    f"Neue Bewerbung im HR-Portal, Vorgang #{application.pk}.\nBitte im geschützten Django-Admin ansehen. Keine Bewerbungsunterlagen per E-Mail.",
                    settings.DEFAULT_FROM_EMAIL, [settings.HR_NOTIFICATION_EMAIL], fail_silently=False,
                )
                application.notification_sent = True
                application.save(update_fields=["notification_sent"])
            except Exception:
                log.exception("HR mail notification failed for application %s", application.pk)
            # Applicant acknowledgement is independent of the internal HR notification.
            # Never include submitted documents or sensitive application details in email.
            try:
                send_mail(
                    "HAMMEL | Eingangsbestätigung Ihrer Bewerbung",
                    (
                        f"Guten Tag {application.full_name},\n\n"
                        "vielen Dank für Ihr Interesse an HAMMEL Recyclingtechnik und "
                        "für Ihre Bewerbung.\n\n"
                        "Wir bestätigen Ihnen, dass Ihre Bewerbung und die über das "
                        "Bewerbungsformular eingereichten Unterlagen bei uns eingegangen sind. "
                        "Unser HR-Team wird Ihre Bewerbung prüfen und sich bei Ihnen melden, "
                        "sobald es Neuigkeiten gibt.\n\n"
                        "Bitte antworten Sie auf diese E-Mail, falls Sie Fragen zu Ihrer "
                        "Bewerbung haben.\n\n"
                        "Freundliche Grüße\n"
                        "Ihr HAMMEL HR-Team\n"
                        "HAMMEL Recyclingtechnik GmbH"
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [application.email],
                    fail_silently=False,
                )
            except Exception:
                log.exception("Applicant confirmation email failed for application %s", application.pk)
            return render(request, "recruiting/apply.html", {"success": True, "job": vacancy})
    else: form = ApplicationForm(vacancy=vacancy)
    return render(request, "recruiting/apply.html", {"form": form, "job": vacancy})

@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_management(request):
    return render(request, "recruiting/staff_panel.html", {
        "applications": Application.objects.select_related("vacancy")[:30],
        "vacancies": Vacancy.objects.all(),
        "departments": ApplicationDepartment.objects.all(),
        "tips": HRTip.objects.all(),
        "new_count": Application.objects.filter(status="new").count(),
    })


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_dashboard(request):
    return render(request, "recruiting/staff_home.html", {
        "vacancy_count": Vacancy.objects.count(),
        "department_count": ApplicationDepartment.objects.count(),
        "tip_count": HRTip.objects.count(),
        "new_count": Application.objects.filter(status="new").count(),
    })


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
def hr_section(request, section):
    if section not in ("stellen", "bereiche", "tipps", "bewerbungen"):
        from django.http import Http404
        raise Http404
    return render(request, "recruiting/staff_panel.html", {
        "section": section,
        "applications": Application.objects.select_related("vacancy")[:100],
        "vacancies": Vacancy.objects.all(),
        "departments": ApplicationDepartment.objects.all(),
        "tips": HRTip.objects.all(),
        "new_count": Application.objects.filter(status="new").count(),
    })


HR_EDITABLE = {
    "vacancy": (Vacancy, ("title", "category", "location", "employment_type", "introduction", "responsibilities", "requirements", "benefits", "published", "sort_order")),
    "department": (ApplicationDepartment, ("name", "active", "sort_order")),
    "tip": (HRTip, ("title", "body", "order", "published")),
    "application": (Application, ("status", "notes")),
}


@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
@require_http_methods(["GET", "POST"])
def hr_edit(request, kind, pk=None):
    from django import forms
    from django.db import models as db_models
    from django.contrib import messages
    from django.contrib.auth.decorators import permission_required
    from django.http import HttpResponseForbidden
    from django.urls import reverse
    if kind not in HR_EDITABLE:
        from django.http import Http404
        raise Http404
    model, fields = HR_EDITABLE[kind]
    perm_action = "change" if pk else "add"
    if not request.user.has_perm(f"recruiting.{perm_action}_{model._meta.model_name}"):
        return HttpResponseForbidden("Keine Berechtigung")
    if kind == "application" and not pk:
        return HttpResponseForbidden("Bewerbungen können nicht manuell angelegt werden")
    obj = get_object_or_404(model, pk=pk) if pk else None
    Form = forms.modelform_factory(model, fields=fields, widgets={
        f.name: forms.Textarea(attrs={"rows": 5}) for f in model._meta.fields if f.name in fields and isinstance(f, db_models.TextField)
    })
    form = Form(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Änderungen wurden gespeichert")
        return redirect("hr_dashboard")
    return render(request, "recruiting/staff_edit.html", {"form": form, "kind": kind, "object": obj})


@login_required
@require_http_methods(["POST"])
@login_required(login_url="hr_login")
@permission_required("recruiting.view_application", raise_exception=True)
@require_http_methods(["POST"])
def hr_delete(request, kind, pk):
    from django.http import Http404, HttpResponseForbidden
    from django.contrib import messages
    if kind not in ("vacancy", "department", "tip"):
        raise Http404
    model, _ = HR_EDITABLE[kind]
    if not request.user.has_perm(f"recruiting.delete_{model._meta.model_name}"):
        return HttpResponseForbidden("Keine Berechtigung")
    get_object_or_404(model, pk=pk).delete()
    messages.success(request, "Eintrag gelöscht")
    return redirect("hr_dashboard")


class HRLoginView(LoginView):
    template_name = "recruiting/hr_login.html"
    redirect_authenticated_user = False

    def get_success_url(self):
        return str(reverse_lazy("hr_dashboard"))

    def form_valid(self, form):
        if not form.get_user().has_perm("recruiting.view_application"):
            form.add_error(None, "Ihr Benutzerkonto hat keinen Zugang zum HR-Portal.")
            return self.form_invalid(form)
        return super().form_valid(form)


class HRLogoutView(LogoutView):
    next_page = reverse_lazy("hr_login")
