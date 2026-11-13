"""Independent HAMMEL Messen dashboard, protected by Django permissions."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from .forms import MesseForm, NewsArticleForm
from .models import Messe, MessePhoto, NewsArticle

def save_gallery(request, messe):
    # Upload several images; remove only those explicitly selected by the editor.
    for photo in request.FILES.getlist("gallery_images"):
        MessePhoto.objects.create(messe=messe, image=photo)
    for photo_id in request.POST.getlist("remove_photos"):
        if photo_id.isdigit():
            MessePhoto.objects.filter(messe=messe, pk=int(photo_id)).delete()

class StaffLoginView(LoginView):
    template_name = "messen/login.html"
    redirect_authenticated_user = True

class StaffLogoutView(LogoutView):
    next_page = reverse_lazy("messen_login")

@login_required(login_url="messen_login")
@permission_required("messen.view_messe", raise_exception=True)
def dashboard(request):
    items = Messe.objects.all().order_by("-start_date", "title")
    return render(request, "messen/dashboard.html", {"items": items, "total": items.count(), "live": items.filter(published=True).count()})

@login_required(login_url="messen_login")
@permission_required("messen.add_messe", raise_exception=True)
def create(request):
    form = MesseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        messe = form.save()
        from translations.services import save_inline
        save_inline(request, messe, form)
        save_gallery(request, messe)
        messages.success(request, "Messe wurde erfolgreich angelegt.")
        return redirect("messen_dashboard")
    return render(request, "messen/form.html", {"form": form, "editing": False})

@login_required(login_url="messen_login")
@permission_required("messen.change_messe", raise_exception=True)
def edit(request, pk):
    obj = get_object_or_404(Messe, pk=pk)
    form = MesseForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        messe = form.save()
        save_gallery(request, messe)
        messages.success(request, "Änderungen wurden gespeichert.")
        return redirect("messen_dashboard")
    return render(request, "messen/form.html", {"form": form, "editing": True, "item": obj, "object": obj})

@login_required(login_url="messen_login")
@permission_required("messen.delete_messe", raise_exception=True)
def delete(request, pk):
    obj = get_object_or_404(Messe, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Messe wurde gelöscht.")
        return redirect("messen_dashboard")
    return render(request, "messen/delete.html", {"item": obj})

@login_required(login_url="messen_login")
def staff_home(request):
    can_messen = request.user.has_perm("messen.view_messe")
    can_news = request.user.has_perm("messen.view_newsarticle")
    can_used = request.user.has_perm("messen.view_usedmachine")
    can_machines = request.user.has_perm("messen.view_machineproduct") or request.user.has_perm("messen.view_machinevariant")
    can_contacts = request.user.has_perm("contacts.view_contactperson") or request.user.has_perm("contacts.view_contactgroup")
    can_partners = request.user.has_perm("partners.view_partner")
    if not (can_messen or can_news or can_used or can_machines or can_contacts or can_partners):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, "messen/staff_home.html", {"can_messen": can_messen, "can_news": can_news, "can_used": can_used, "can_machines": can_machines, "can_contacts": can_contacts, "can_partners": can_partners})

@login_required(login_url="messen_login")
@permission_required("messen.view_newsarticle", raise_exception=True)
def news_dashboard(request):
    items = NewsArticle.objects.all()
    return render(request, "messen/news_dashboard.html", {"items": items, "total": items.count(), "live": items.filter(published=True).count()})

@login_required(login_url="messen_login")
@permission_required("messen.add_newsarticle", raise_exception=True)
def news_create(request):
    form = NewsArticleForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        article = form.save()
        messages.success(request, "Beitrag wurde gespeichert. Weitere Sprachversionen können jetzt bearbeitet werden.")
        return redirect("news_edit", pk=article.pk)
    return render(request, "messen/news_form.html", {"form": form, "editing": False})

@login_required(login_url="messen_login")
@permission_required("messen.change_newsarticle", raise_exception=True)
def news_edit(request, pk):
    item = get_object_or_404(NewsArticle, pk=pk)
    form = NewsArticleForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        from translations.services import save_inline
        save_inline(request, saved, form)
        messages.success(request, "Änderungen wurden gespeichert.")
        return redirect("news_edit", pk=saved.pk)
    return render(request, "messen/news_form.html", {"form": form, "editing": True, "item": item, "object": item})

@login_required(login_url="messen_login")
@permission_required("messen.delete_newsarticle", raise_exception=True)
def news_delete(request, pk):
    item = get_object_or_404(NewsArticle, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Beitrag wurde gelöscht.")
        return redirect("news_dashboard")
    return render(request, "messen/news_delete.html", {"item": item})


from .models import UsedMachine, UsedMachinePhoto
from .forms import UsedMachineForm

@login_required(login_url="messen_login")
@permission_required("messen.view_usedmachine", raise_exception=True)
def used_dashboard(request):
    items = UsedMachine.objects.all()
    return render(request, "messen/used_dashboard.html", {"items": items, "total": items.count(), "live": items.filter(published=True).count()})

def save_used_photos(request, machine):
    for f in request.FILES.getlist("gallery_images"):
        UsedMachinePhoto.objects.create(machine=machine, image=f)
    for photo_id in request.POST.getlist("remove_photos"):
        if photo_id.isdigit():
            UsedMachinePhoto.objects.filter(machine=machine, pk=int(photo_id)).delete()

@login_required(login_url="messen_login")
@permission_required("messen.add_usedmachine", raise_exception=True)
def used_create(request):
    form = UsedMachineForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        machine = form.save(); save_used_photos(request, machine)
        messages.success(request, "Maschine wurde angelegt.")
        return redirect("used_dashboard")
    return render(request, "messen/used_form.html", {"form": form, "editing": False})

@login_required(login_url="messen_login")
@permission_required("messen.change_usedmachine", raise_exception=True)
def used_edit(request, pk):
    machine = get_object_or_404(UsedMachine, pk=pk)
    form = UsedMachineForm(request.POST or None, request.FILES or None, instance=machine)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        from translations.services import save_inline
        save_inline(request, saved, form)
        save_used_photos(request, machine)
        messages.success(request, "Maschine wurde aktualisiert.")
        return redirect("used_dashboard")
    return render(request, "messen/used_form.html", {"form": form, "editing": True, "item": machine, "object": machine})

@login_required(login_url="messen_login")
@permission_required("messen.delete_usedmachine", raise_exception=True)
def used_delete(request, pk):
    machine = get_object_or_404(UsedMachine, pk=pk)
    if request.method == "POST":
        machine.delete(); messages.success(request, "Maschine wurde gelöscht.")
        return redirect("used_dashboard")
    return render(request, "messen/used_delete.html", {"item": machine})

# Separate, permission-protected sales interface for new machines and their versions.
from .models import MachineProduct, MachineVariant, RecyclingArea, RecyclingMaterial, MachineVariantPhoto, MachineVariantRevision, MachineVariantDraft
from .forms import MachineProductForm, MachineVariantForm

@login_required(login_url="messen_login")
def machine_dashboard(request):
    if not (request.user.has_perm("messen.view_machineproduct") or request.user.has_perm("messen.view_machinevariant")):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, "messen/machine_staff_dashboard.html", {
        "products": MachineProduct.objects.prefetch_related("variants").all(),
        "variants": MachineVariant.objects.select_related("product").all(),
        "can_add_product": request.user.has_perm("messen.add_machineproduct"),
        "can_add_variant": request.user.has_perm("messen.add_machinevariant"),
    })

def _machine_form(request, model, form_class, permission, instance=None):
    from django.core.exceptions import PermissionDenied
    from django.db import transaction
    from django.forms.models import model_to_dict
    from .models import RecyclingArea, RecyclingMaterial
    if not request.user.has_perm(permission):
        raise PermissionDenied
    is_variant = model == "Maschinenvariante"
    # A draft is private to the editing workflow and never updates the published object.
    draft = MachineVariantDraft.objects.filter(variant=instance).first() if is_variant and instance else None
    initial = draft.values if draft and request.GET.get("draft") == "1" else None
    form = form_class(request.POST or None, request.FILES or None, instance=instance, initial=initial)
    if request.method == "POST" and is_variant and request.POST.get("editor_action") == "preview":
        # Render current text values without committing the object or publication state.
        if form.is_valid():
            from django.template.response import TemplateResponse
            from .models import RecyclingArea
            preview_variant = form.save(commit=False)
            preview_variant.pk = instance.pk if instance else None
            selected_ids = [int(x) for x in request.POST.getlist("materials") if x.isdigit()]
            rows=[]
            for area in RecyclingArea.objects.prefetch_related("materials"):
                materials=[m for m in area.materials.all() if m.pk in selected_ids]
                if materials: rows.append((area,materials))
            return TemplateResponse(request,"messen/machine_variant_detail.html",{
                "variant":preview_variant,"product":preview_variant.product,
                "application_rows":rows,"custom_rows":[],"editor_preview":True})
    if request.method == "POST" and is_variant and request.POST.get("editor_action") == "draft":
        if instance:
            allowed = [name for name in form.fields if name not in ("image","hero_video","technical_drawing")]
            values = {name:request.POST.get(name, "") for name in allowed if name in request.POST}
            MachineVariantDraft.objects.update_or_create(variant=instance, defaults={"values":values,"author":request.user})
            messages.success(request,"Entwurf gespeichert. Die öffentliche Seite bleibt unverändert.")
            return redirect("staff_machine_variant_edit",pk=instance.pk)
        else:
            messages.error(request,"Bitte speichern Sie zuerst die neue Variante, bevor Sie einen Entwurf anlegen.")
    if request.method == "POST" and request.POST.get("editor_action") not in ("preview","draft") and form.is_valid():
        with transaction.atomic():
            before = model_to_dict(instance,exclude=["materials"]) if is_variant and instance else {}
            if before:
                before={k:str(v) if not isinstance(v,(int,float,bool,str,type(None))) else v for k,v in before.items()}
            obj=form.save()
            from translations.services import save_inline
            save_inline(request, obj, form)
            if is_variant:
                selected={int(x) for x in request.POST.getlist("materials") if x.isdigit()}
                area_ids={int(x) for x in request.POST.getlist("areas") if x.isdigit()}
                chosen=list(RecyclingMaterial.objects.filter(pk__in=selected,area_id__in=area_ids))
                for area in RecyclingArea.objects.filter(pk__in=area_ids):
                    for line in request.POST.get("new_material_%s"%area.pk,"").splitlines():
                        label=" ".join(line.strip().split())[:180]
                        if label:
                            material,_=RecyclingMaterial.objects.get_or_create(area=area,name=label)
                            chosen.append(material)
                obj.materials.set(chosen)
                for photo in request.FILES.getlist("gallery_images"):
                    MachineVariantPhoto.objects.create(variant=obj,image=photo,position=obj.gallery.count())
                for raw in request.POST.getlist("remove_photos"):
                    if raw.isdigit(): MachineVariantPhoto.objects.filter(variant=obj,pk=int(raw)).delete()
                positions=request.POST.get("gallery_order","").split(",")
                for position,raw in enumerate(positions):
                    if raw.isdigit():MachineVariantPhoto.objects.filter(variant=obj,pk=int(raw)).update(position=position)
                cover=request.POST.get("cover_photo")
                if cover and cover.isdigit():
                    obj.gallery.update(is_cover=False)
                    obj.gallery.filter(pk=int(cover)).update(is_cover=True)
                if before:MachineVariantRevision.objects.create(variant=obj,author=request.user,action="saved",snapshot=before)
                MachineVariantDraft.objects.filter(variant=obj).delete()
            messages.success(request,"Maschinendaten gespeichert.")
            return redirect("staff_machine_variant_edit",pk=obj.pk) if is_variant else redirect("staff_machine_dashboard")
    area_rows=[]
    if is_variant:
        assigned=set(instance.materials.values_list("pk",flat=True)) if instance else set()
        if request.method=="POST":
            assigned={int(x) for x in request.POST.getlist("materials") if x.isdigit()}
            active={int(x) for x in request.POST.getlist("areas") if x.isdigit()}
        else:
            active=set(RecyclingArea.objects.filter(materials__pk__in=assigned).values_list("pk",flat=True))
        for area in RecyclingArea.objects.prefetch_related("materials"):
            area_rows.append({"area":area,"items":area.materials.all(),"active":area.pk in active,
                              "selected":assigned,"new_text":request.POST.get("new_material_%s"%area.pk,"")})
    completion=[]
    if is_variant:
        for key,label in (("name","Modellbezeichnung"),("product","Baureihe"),("description","Beschreibung"),("engine","Motor"),("drive","Antrieb / Leistung"),("weight","Gewicht"),("image","Maschinenfoto"),("datasheet_url","Datenblatt"),("technical_drawing","Technische Zeichnung"),("hero_video","Hero-Video")):
            val=getattr(instance,key,None) if instance else None
            if key=="image":val=val or (instance.image_url if instance else None)
            if key=="technical_drawing":val=val or (instance.technical_drawing_url if instance else None)
            if key=="hero_video":val=val or (instance.hero_video_url if instance else None)
            completion.append({"name":label,"filled":bool(val)})
    sources=MachineVariant.objects.exclude(pk=instance.pk if instance else None).select_related("product").order_by("product__model_name","name") if is_variant else []
    return render(request,"messen/machine_staff_form.html",{
        "form":form,"object":instance,"kind":model,"area_rows":area_rows,"completion":completion,
        "completion_done":sum(x["filled"] for x in completion),"completion_total":len(completion),
        "sources":sources,"gallery":instance.gallery.all() if is_variant and instance else [],
        "revisions":instance.revisions.select_related("author")[:12] if is_variant and instance else [],
        "draft":draft,
    })

@login_required(login_url="messen_login")
def machine_product_create(request):
    return _machine_form(request, "Maschinenmodell", MachineProductForm, "messen.add_machineproduct")

@login_required(login_url="messen_login")
def machine_product_edit(request, pk):
    return _machine_form(request, "Maschinenmodell", MachineProductForm, "messen.change_machineproduct", get_object_or_404(MachineProduct, pk=pk))

@login_required(login_url="messen_login")
def machine_variant_create(request):
    return _machine_form(request, "Maschinenvariante", MachineVariantForm, "messen.add_machinevariant")

@login_required(login_url="messen_login")
def machine_variant_edit(request, pk):
    return _machine_form(request, "Maschinenvariante", MachineVariantForm, "messen.change_machinevariant", get_object_or_404(MachineVariant, pk=pk))


from django.utils.text import slugify
from .models import MachineField, MachineFieldSetting, MachineFieldValue
from django.db import transaction

@login_required(login_url="messen_login")
def machine_fields_manage(request):
    if not request.user.has_perm("messen.change_machinevariant"):
        raise PermissionDenied
    scope = request.GET.get("scope", "global")
    target = None
    if scope == "series": target = get_object_or_404(MachineProduct, pk=request.GET.get("id"))
    elif scope == "variant": target = get_object_or_404(MachineVariant, pk=request.GET.get("id"))
    else: scope = "global"
    if request.method == "POST":
        action=request.POST.get("action")
        if action == "add":
            label=request.POST.get("label","").strip()[:150]
            section=request.POST.get("section","technical")
            ftype=request.POST.get("field_type","text")
            if label and section in dict(MachineField.SECTIONS) and ftype in dict(MachineField.FIELD_TYPES):
                base=slugify(label)[:70] or "custom"; key=base; counter=2
                while MachineField.objects.filter(key=key).exists():
                    key=f"{base}-{counter}"; counter+=1
                MachineField.objects.create(key=key,label=label,section=section,field_type=ftype,position=MachineField.objects.count()+1)
        elif action in ("save","archive","restore"):
            field=get_object_or_404(MachineField,pk=request.POST.get("field_id"))
            if action in ("archive","restore") and not field.is_system:
                field.archived=(action=="archive");field.save(update_fields=["archived"])
            elif action=="save":
                if scope=="global":
                    section=request.POST.get("section",field.section)
                    if section in dict(MachineField.SECTIONS):field.section=section
                    field.label=request.POST.get("label",field.label).strip()[:150] or field.label
                    try:field.position=max(0,int(request.POST.get("position",field.position)))
                    except ValueError:pass
                    field.show_public="show_public" in request.POST
                    field.show_compare="show_compare" in request.POST
                    field.save()
                else:
                    kwargs={"variant":target} if scope=="variant" else {"product":target}
                    setting,_=MachineFieldSetting.objects.get_or_create(field=field,**kwargs)
                    setting.show_public={"inherit":None,"yes":True,"no":False}.get(request.POST.get("show_public"),None)
                    setting.show_compare={"inherit":None,"yes":True,"no":False}.get(request.POST.get("show_compare"),None)
                    setting.save()
        messages.success(request,"Feldverwaltung aktualisiert.")
        return redirect(request.get_full_path())
    rows=[]
    for field in MachineField.objects.all():
        setting=None
        if scope!="global":
            setting=MachineFieldSetting.objects.filter(field=field,**({"variant":target} if scope=="variant" else {"product":target})).first()
        rows.append({"field":field,"public_setting":("inherit" if not setting or setting.show_public is None else "yes" if setting.show_public else "no"),"compare_setting":("inherit" if not setting or setting.show_compare is None else "yes" if setting.show_compare else "no")})
    return render(request,"messen/machine_fields_manage.html",{"rows":rows,"scope":scope,"target":target,"sections":MachineField.SECTIONS,"types":MachineField.FIELD_TYPES})


def machine_field_visibility(field, variant, compare=False):
    if not field or field.archived:return False
    result=field.show_compare if compare else field.show_public
    attr="show_compare" if compare else "show_public"
    series_setting=MachineFieldSetting.objects.filter(field=field,product=variant.product,variant__isnull=True).first()
    if series_setting and getattr(series_setting,attr) is not None:result=getattr(series_setting,attr)
    variant_setting=MachineFieldSetting.objects.filter(field=field,variant=variant).first()
    if variant_setting and getattr(variant_setting,attr) is not None:result=getattr(variant_setting,attr)
    return result

@login_required(login_url="messen_login")
def machine_custom_values(request,pk):
    if not request.user.has_perm("messen.change_machinevariant"):raise PermissionDenied
    variant=get_object_or_404(MachineVariant,pk=pk)
    fields=list(MachineField.objects.filter(is_system=False,archived=False))
    if request.method=="POST":
        for field in fields:
            value,_=MachineFieldValue.objects.get_or_create(field=field,variant=variant)
            if field.field_type in ("file","image","video"):
                if request.POST.get("clear_"+str(field.pk))=="1":value.file_value=""
                if request.FILES.get("file_"+str(field.pk)):value.file_value=request.FILES["file_"+str(field.pk)]
            else:
                value.text_value=("Ja" if request.POST.get("value_"+str(field.pk)) else "Nein") if field.field_type=="boolean" else request.POST.get("value_"+str(field.pk),"")
            value.save()
        messages.success(request,"Zusätzliche Felder gespeichert.")
        return redirect("staff_machine_custom_values",pk=pk)
    existing={v.field_id:v for v in variant.custom_values.all()}
    return render(request,"messen/machine_custom_values.html",{"variant":variant,"rows":[{"field":f,"value":existing.get(f.pk)} for f in fields]})


@login_required(login_url="messen_login")
def machine_variant_copy(request,pk):
    from django.core.exceptions import PermissionDenied
    if not request.user.has_perm("messen.add_machinevariant"):raise PermissionDenied
    source=get_object_or_404(MachineVariant,pk=pk)
    if request.method!="POST":return redirect("staff_machine_variant_create")
    from django.db import transaction
    with transaction.atomic():
        copied=MachineVariant.objects.get(pk=source.pk)
        copied.pk=None
        copied.name=source.name+" – Kopie"
        copied.published=False
        copied.image=None
        copied.hero_video=None
        copied.technical_drawing=None
        copied.save()
        copied.materials.set(source.materials.all())
    messages.success(request,"Kopie erstellt. Bitte prüfen Sie alle Angaben und ergänzen Sie die Dokumente.")
    return redirect("staff_machine_variant_edit",pk=copied.pk)

@login_required(login_url='messen_login')
@permission_required('messen.view_homepageshowcase', raise_exception=True)
def showcase_dashboard(request):
    from .models import HomepageShowcase
    return render(request, 'messen/showcase_dashboard.html', {'items': HomepageShowcase.objects.all()})

@login_required(login_url='messen_login')
@permission_required('messen.change_homepageshowcase', raise_exception=True)
def showcase_edit(request, pk):
    from django import forms
    from .models import HomepageShowcase, MachineProduct
    class ShowcaseForm(forms.ModelForm):
        class Meta:
            model = HomepageShowcase
            fields = ['category','product','eyebrow','headline','description','other_models','image','image_path','button_text','button_url','position','is_default','published']
            widgets = {'description': forms.Textarea(attrs={'rows':3})}
    obj = get_object_or_404(HomepageShowcase, pk=pk)
    form = ShowcaseForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        saved = form.save()
        if saved.is_default:
            HomepageShowcase.objects.exclude(pk=saved.pk).update(is_default=False)
        messages.success(request, 'Showcase gespeichert.')
        return redirect('showcase_dashboard')
    return render(request, 'messen/showcase_edit.html', {'form':form, 'item':obj})


@login_required(login_url="messen_login")
@permission_required("messen.change_messe", raise_exception=True)
def messe_language_editor(request, pk, lang):
    """Messe-only language/review workflow. HRPortal and shared editors stay untouched."""
    from django.contrib.contenttypes.models import ContentType
    from django.db import transaction
    from django.http import Http404
    from translations.models import ContentTranslation
    from .models import MesseTranslationChange
    from translations.services import fields_for, fingerprint
    messe = get_object_or_404(Messe, pk=pk)
    if request.method == "POST" and lang == "review":
        if not request.user.has_perm("messen.change_messe"):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        if request.POST.get("visibility_action") == "save":
            # DE is the original; the other languages are individually configurable.
            visible = {code: code in request.POST.getlist("visible_languages") for code in ("en", "fr", "es", "it")}
            messe.language_visibility = visible
            messe.save(update_fields=["language_visibility"])
            messages.success(request, "Sichtbarkeit der Sprachversionen gespeichert.")
            return redirect("messen_language_editor", pk=pk, lang="review")
        if request.POST.get("publication_confirm") != "on":
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("Bitte bestätigen Sie die Prüfung vor der Änderung des Veröffentlichungsstatus.")
        action = request.POST.get("publication_action")
        if action not in {"publish", "unpublish"}:
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("Ungültige Veröffentlichungsaktion.")
        messe.published = action == "publish"
        messe.save(update_fields=["published", "updated_at"])
        messages.success(request, "Messe veröffentlicht." if messe.published else "Messe deaktiviert.")
        return redirect("messen_language_editor", pk=pk, lang="review")
    if lang not in {"en", "fr", "es", "it", "review"}:
        raise Http404
    # Messe-specific fields: do not change shared translation rules or HRPortal.
    fields = [messe._meta.get_field(name) for name in ("title", "booth", "city", "country", "description")]
    ct = ContentType.objects.get_for_model(Messe)
    translations = {(t.language, t.field_name): t for t in ContentTranslation.objects.filter(content_type=ct, object_id=messe.pk)}
    if request.method == "POST" and lang != "review":
        with transaction.atomic():
            for field in fields:
                value = request.POST.get("translation_" + field.name, "")
                if len(value) > 30000:
                    messages.error(request, "Ein Text ist zu lang (maximal 30.000 Zeichen).")
                    return redirect("messen_language_editor", pk=pk, lang=lang)
                previous = translations.get((lang, field.name))
                requested_status = request.POST.get("status_" + field.name, "draft")
                if requested_status not in {"draft", "review", "published"}:
                    requested_status = "draft"
                original_hash = fingerprint(getattr(messe, field.name))
                changed = previous is None or previous.text != value
                confirmed = request.POST.get("confirm_" + field.name) == "on"
                source_hash = original_hash if changed or confirmed else previous.source_hash
                if previous and previous.source_hash != original_hash and not (changed or confirmed) and requested_status == "published":
                    requested_status = "review"
                ContentTranslation.objects.update_or_create(
                    content_type=ct, object_id=messe.pk, language=lang, field_name=field.name,
                    defaults={"text": value, "status": requested_status if value.strip() else "draft", "source_hash": source_hash, "updated_by": request.user},
                )
                final_status = requested_status if value.strip() else "draft"
                if previous is None:
                    old_text, old_status = "", ""
                else:
                    old_text, old_status = previous.text, previous.status
                if old_text != value or old_status != final_status:
                    MesseTranslationChange.objects.create(
                        messe=messe, author=request.user, language=lang,
                        field_name=field.name, field_label=str(field.verbose_name).capitalize(),
                        old_text=old_text, new_text=value, old_status=old_status, new_status=final_status,
                    )
        messages.success(request, "Sprachversion gespeichert.")
        return redirect("messen_language_editor", pk=pk, lang=lang)
    rows = []
    for field in fields:
        original = str(getattr(messe, field.name) or "")
        if lang == "review":
            cells = []
            for code in ("en", "fr", "es", "it"):
                t = translations.get((code, field.name))
                cells.append({"code": code, "text": t.text if t else "", "status": t.status if t else "draft", "stale": bool(t and t.text.strip() and t.source_hash != fingerprint(original))})
            rows.append({"name": field.name, "label": str(field.verbose_name).capitalize(), "original": original, "cells": cells})
        else:
            t = translations.get((lang, field.name))
            rows.append({"name": field.name, "label": str(field.verbose_name).capitalize(), "original": original, "text": t.text if t else "", "status": t.status if t else "draft", "stale": bool(t and t.text.strip() and t.source_hash != fingerprint(original))})
    review_summary = []
    if lang == "review":
        language_names = {"en": "English", "fr": "Français", "es": "Español", "it": "Italiano"}
        for code, name in language_names.items():
            counts = {"ready": 0, "review": 0, "missing": 0, "stale": 0}
            for row in rows:
                cell = next(c for c in row["cells"] if c["code"] == code)
                if not cell["text"].strip():
                    counts["missing"] += 1
                elif cell["stale"]:
                    counts["stale"] += 1
                elif cell["status"] == "published":
                    counts["ready"] += 1
                else:
                    counts["review"] += 1
            total = sum(counts.values())
            review_summary.append({"code": code, "name": name, **counts,
                                   "total": total, "progress": round(counts["ready"] * 100 / total) if total else 0})
    history_entries = []
    history_months = []
    history_years = []
    selected_month = request.GET.get("month", "")
    selected_year = request.GET.get("year", "")
    if lang == "review":
        from django.utils.formats import date_format
        from datetime import date
        all_changes = MesseTranslationChange.objects.filter(messe=messe).select_related("author")
        history_years = sorted({d.year for d in all_changes.dates("created_at", "year")}, reverse=True)
        history_months = [{"value": str(m), "label": date_format(date(2024, m, 1), "F")} for m in range(1, 13)]
        if selected_year.isdigit() and len(selected_year) == 4:
            all_changes = all_changes.filter(created_at__year=int(selected_year))
        if selected_month.isdigit() and 1 <= int(selected_month) <= 12:
            all_changes = all_changes.filter(created_at__month=int(selected_month))
        history_entries = list(all_changes[:100])
    return render(request, "messen/messe_languages.html", {"item": messe, "visible_languages": messe.language_visibility or {}, "enabled_languages": [code for code in ("en", "fr", "es", "it") if (messe.language_visibility or {}).get(code, False)], "publication_languages": [("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano")], "lang": lang, "rows": rows, "review": lang == "review", "review_summary": review_summary, "history_entries": history_entries, "history_years": history_years, "history_months": history_months, "selected_month": selected_month, "selected_year": selected_year})


@login_required(login_url="messen_login")
@permission_required("messen.change_newsarticle", raise_exception=True)
def news_language_editor(request, pk, lang):
    """News-only language editor; never changes HRPortal or Messen translation records."""
    from datetime import date
    from django.contrib.contenttypes.models import ContentType
    from django.db import transaction
    from django.http import Http404
    from django.utils.formats import date_format
    from translations.models import ContentTranslation
    from translations.services import fingerprint
    from .models import NewsTranslationChange

    if lang not in {"en", "fr", "es", "it", "review"}:
        raise Http404
    article = get_object_or_404(NewsArticle, pk=pk)
    if request.method == "POST" and lang == "review":
        if request.POST.get("visibility_action") == "save":
            # DE is the original; the other languages are individually configurable.
            visible = {code: code in request.POST.getlist("visible_languages") for code in ("en", "fr", "es", "it")}
            article.language_visibility = visible
            article.save(update_fields=["language_visibility"])
            messages.success(request, "Sichtbarkeit der Sprachversionen gespeichert.")
            return redirect("news_language_editor", pk=pk, lang="review")
        if request.POST.get("publication_confirm") != "on":
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("Bitte bestätigen Sie die Prüfung vor der Änderung des Veröffentlichungsstatus.")
        action = request.POST.get("publication_action")
        if action not in {"publish", "unpublish"}:
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("Ungültige Veröffentlichungsaktion.")
        article.published = action == "publish"
        article.save(update_fields=["published"])
        messages.success(request, "Beitrag veröffentlicht." if article.published else "Beitrag deaktiviert.")
        return redirect("news_language_editor", pk=pk, lang="review")
    fields = [article._meta.get_field(name) for name in ("title", "teaser", "body")]
    ct = ContentType.objects.get_for_model(NewsArticle)
    translations = {(t.language, t.field_name): t for t in ContentTranslation.objects.filter(content_type=ct, object_id=article.pk)}
    if request.method == "POST":
        if lang == "review":
            raise Http404
        submitted = []
        for field in fields:
            value = request.POST.get("translation_" + field.name, "")
            if len(value) > 100000:
                messages.error(request, "Der Text ist zu lang (maximal 100.000 Zeichen).")
                return redirect("news_language_editor", pk=pk, lang=lang)
            status = request.POST.get("status_" + field.name, "draft")
            if status not in {"draft", "review", "published"}:
                status = "draft"
            submitted.append((field, value, status))
        with transaction.atomic():
            for field, value, status in submitted:
                previous = translations.get((lang, field.name))
                old_text = previous.text if previous else ""
                old_status = previous.status if previous else ""
                original_hash = fingerprint(getattr(article, field.name))
                changed = previous is None or old_text != value
                confirmed = request.POST.get("confirm_" + field.name) == "on"
                source_hash = original_hash if changed or confirmed else previous.source_hash
                if previous and previous.source_hash != original_hash and not (changed or confirmed) and status == "published":
                    status = "review"
                final_status = status if value.strip() else "draft"
                ContentTranslation.objects.update_or_create(
                    content_type=ct, object_id=article.pk, language=lang, field_name=field.name,
                    defaults={"text": value, "status": final_status, "source_hash": source_hash, "updated_by": request.user},
                )
                if old_text != value or old_status != final_status:
                    NewsTranslationChange.objects.create(
                        article=article, author=request.user, language=lang,
                        field_name=field.name, field_label=str(field.verbose_name).capitalize(),
                        old_text=old_text, new_text=value, old_status=old_status, new_status=final_status,
                    )
        messages.success(request, "Sprachversion gespeichert.")
        return redirect("news_language_editor", pk=pk, lang=lang)

    rows = []
    for field in fields:
        original = str(getattr(article, field.name) or "")
        if lang == "review":
            cells = []
            for code in ("en", "fr", "es", "it"):
                t = translations.get((code, field.name))
                cells.append({"code": code, "text": t.text if t else "", "status": t.status if t else "draft",
                              "stale": bool(t and t.text.strip() and t.source_hash != fingerprint(original))})
            rows.append({"name": field.name, "label": str(field.verbose_name).capitalize(), "original": original, "cells": cells})
        else:
            t = translations.get((lang, field.name))
            rows.append({"name": field.name, "label": str(field.verbose_name).capitalize(), "original": original,
                         "text": t.text if t else "", "status": t.status if t else "draft",
                         "stale": bool(t and t.text.strip() and t.source_hash != fingerprint(original))})
    summary = []
    history_entries, history_years, history_months = [], [], []
    selected_month, selected_year = request.GET.get("month", ""), request.GET.get("year", "")
    if lang == "review":
        for code, name in (("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano")):
            counts = {"ready": 0, "review": 0, "missing": 0, "stale": 0}
            for row in rows:
                cell = next(c for c in row["cells"] if c["code"] == code)
                if not cell["text"].strip(): counts["missing"] += 1
                elif cell["stale"]: counts["stale"] += 1
                elif cell["status"] == "published": counts["ready"] += 1
                else: counts["review"] += 1
            total = sum(counts.values())
            summary.append({"code": code, "name": name, **counts, "total": total})
        changes = NewsTranslationChange.objects.filter(article=article).select_related("author")
        history_years = sorted({d.year for d in changes.dates("created_at", "year")}, reverse=True)
        history_months = [{"value": str(m), "label": date_format(date(2024, m, 1), "F")} for m in range(1, 13)]
        if selected_year.isdigit() and len(selected_year) == 4:
            changes = changes.filter(created_at__year=int(selected_year))
        if selected_month.isdigit() and 1 <= int(selected_month) <= 12:
            changes = changes.filter(created_at__month=int(selected_month))
        history_entries = list(changes[:100])
    return render(request, "messen/news_languages.html", {
        "item": article, "visible_languages": article.language_visibility or {}, "enabled_languages": [code for code in ("en", "fr", "es", "it") if (article.language_visibility or {}).get(code, False)], "publication_languages": [("en", "English"), ("fr", "Français"), ("es", "Español"), ("it", "Italiano")], "lang": lang, "rows": rows, "review": lang == "review", "review_summary": summary,
        "history_entries": history_entries, "history_years": history_years, "history_months": history_months,
        "selected_month": selected_month, "selected_year": selected_year,
    })


@login_required(login_url="messen_login")
@permission_required("messen.view_messe", raise_exception=True)
def messen_staff_preview(request, pk):
    """Staff-only preview, including unpublished fairs; never changes publication state."""
    item = get_object_or_404(Messe, pk=pk)
    return render(request, "messen/messe_staff_preview.html", {"item": item})


@login_required(login_url="messen_login")
@permission_required("messen.view_newsarticle", raise_exception=True)
def news_staff_preview(request, pk):
    """Staff-only article preview, including unpublished stories."""
    article = get_object_or_404(NewsArticle, pk=pk)
    related = NewsArticle.objects.none()
    return render(request, "messen/news_story.html", {"article": article, "related": related})
