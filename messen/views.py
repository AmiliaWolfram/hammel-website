"""Website page whitelist and published events feed."""
from pathlib import Path
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.views.decorators.http import require_GET
from .models import Messe

PAGES = {"", "agb", "aeb", "impressum", "datenschutz", "unternehmen", "maschinen", "loesungen", "weltweit", "service", "karriere", "kontakt", "aktuelles", "was-uns-bewegt", "service/gebrauchtmaschinen", "service/mietpark", "service/transport"}

@require_GET
def website_page(request, page=""):
    if page not in PAGES:
        raise Http404
    file = Path(settings.BASE_DIR) / "website" / page / "index.html"
    if not file.is_file():
        raise Http404
    if page == "":
        import re
        from django.template.loader import render_to_string
        from .models import HomepageShowcase
        items = list(HomepageShowcase.objects.filter(published=True).select_related('product'))
        html = file.read_text(encoding='utf-8')
        default = next((item for item in items if item.is_default), items[0] if items else None)
        showcase_html = render_to_string('messen/showcase_public.html', {'showcase': items, 'initial_id': default.pk if default else None}, request=request)
        html, count = re.subn(r'<section\b[^>]*\bid="machines"[^>]*>.*?</section>', lambda m: showcase_html, html, count=1, flags=re.S)
        if count != 1:
            raise RuntimeError('Homepage showcase section not found')
        return HttpResponse(html, content_type='text/html; charset=utf-8')
    if page == "service":
        from .models import MachineProduct
        from django.utils.html import escape
        import re
        html = file.read_text(encoding="utf-8")
        products = list(MachineProduct.objects.filter(published=True, category="vorbrecher"))
        links = []
        for model in ("VB 450", "VB 650", "VB 750", "VB 850", "VB 950"):
            product = next((p for p in products if re.search(r"\b" + re.escape(model).replace(r"\ ", r"\s*") + r"\b", p.model_name, re.I)), None)
            if product is not None:
                links.append(f'<a class="service-rental-list__link" href="/maschinen/modell/{product.pk}/"><span class="service-rental-list__name">{escape(model)}</span><span class="service-rental-list__detail">MODELLE ENTDECKEN</span></a>')
            else:
                links.append(f'<a class="service-rental-list__link" href="/maschinen/"><span class="service-rental-list__name">{escape(model)}</span><span class="service-rental-list__detail">MASCHINEN ANSEHEN</span></a>')
        html = html.replace("<!-- SERVICE_RENTAL_MACHINE_LINKS -->", "".join(links))
        return HttpResponse(html, content_type="text/html; charset=utf-8")
    return HttpResponse(file.read_bytes(), content_type="text/html; charset=utf-8")

@require_GET
def published_messen(request):
    events = Messe.objects.filter(published=True).prefetch_related("photos").order_by("start_date", "title")
    return JsonResponse([{
        "title": e.title,
        "start_date": e.start_date.isoformat(),
        "end_date": e.end_date.isoformat(),
        "city": e.city,
        "country": e.country,
        "booth": e.booth,
        "description": e.description,
        "url": e.url,
        "image": e.image.url if e.image else None,
        "photos": [{"image": p.image.url, "caption": p.caption} for p in e.photos.all()],
    } for e in events], safe=False)


@require_GET
def published_news(request):
    from .models import NewsArticle
    articles = NewsArticle.objects.filter(published=True)
    return JsonResponse([{"title": a.title, "teaser": a.teaser, "body": a.body, "category": a.category, "date": a.published_at.isoformat(), "image": a.image.url if a.image else None, "url": f"/was-uns-bewegt/story/{a.pk}/{slugify(a.title)}/", "featured": a.featured} for a in articles], safe=False)


@require_GET
def news_story(request, pk, slug):
    from .models import NewsArticle
    article = get_object_or_404(NewsArticle, pk=pk, published=True)
    canonical = slugify(article.title) or 'story'
    if slug != canonical:
        from django.shortcuts import redirect
        return redirect('news_story', pk=article.pk, slug=canonical, permanent=True)
    related = NewsArticle.objects.filter(published=True, category=article.category).exclude(pk=article.pk)[:3]
    return render(request, 'messen/news_story.html', {'article': article, 'related': related})


@require_GET
def news_story(request, pk, slug):
    from .models import NewsArticle
    article = get_object_or_404(NewsArticle, pk=pk, published=True)
    canonical = slugify(article.title) or 'story'
    if slug != canonical:
        from django.shortcuts import redirect
        return redirect('news_story', pk=article.pk, slug=canonical, permanent=True)
    related = NewsArticle.objects.filter(published=True, category=article.category).exclude(pk=article.pk)[:3]
    return render(request, 'messen/news_story.html', {'article': article, 'related': related})


@require_GET
def used_machines(request):
    from .models import UsedMachine
    items = UsedMachine.objects.filter(published=True).prefetch_related("photos")
    return JsonResponse([{"id": m.pk, "title": m.title, "serial_number": m.serial_number,
        "build_year": m.build_year, "build_month": m.build_month, "operating_hours": m.operating_hours,
        "engine": m.engine, "power": m.power, "shafts": m.shafts, "equipment": m.equipment,
        "weight": m.weight, "condition": m.condition, "description": m.description, "image": m.image.url if m.image else None,
        "photos": [{"image": p.image.url, "caption": p.caption} for p in m.photos.all()],
        "video_url": m.video_url, "url": f"/service/gebrauchtmaschinen/maschine/{m.pk}/"} for m in items], safe=False)

@require_GET
def used_machine_detail(request, pk):
    from .models import UsedMachine
    machine = get_object_or_404(UsedMachine.objects.prefetch_related("photos"), pk=pk, published=True)
    return render(request, "messen/used_detail.html", {"machine": machine})


@require_GET
def machine_catalog(request):
    from .models import MachineProduct, UsedMachine
    return render(request, "messen/machine_catalog.html", {
        "products": MachineProduct.objects.filter(published=True),
        "used": UsedMachine.objects.filter(published=True),
        "categories": MachineProduct.CATEGORIES,
    })

@require_GET
def machine_product_detail(request, pk):
    from .models import MachineProduct
    product = get_object_or_404(MachineProduct.objects.prefetch_related("variants"), pk=pk, published=True)
    return render(request, "messen/machine_product_detail.html", {"product": product, "variants": product.variants.filter(published=True)})

@require_GET
def machine_variant_detail(request, pk):
    from .models import MachineVariant
    variant = get_object_or_404(MachineVariant.objects.select_related("product"), pk=pk, published=True, product__published=True)
    from .models import RecyclingArea
    areas = RecyclingArea.objects.prefetch_related("materials").all()
    chosen_ids = set(variant.materials.values_list("pk", flat=True))
    rows = [(area, [m for m in area.materials.all() if m.pk in chosen_ids]) for area in areas]
    rows = [(area, items) for area, items in rows if items]
    from .models import MachineField, MachineFieldValue
    from .staff_views import machine_field_visibility
    definitions = list(MachineField.objects.filter(archived=False))
    visibility = {f.key: machine_field_visibility(f, variant) for f in definitions}
    custom_rows = []
    for val in MachineFieldValue.objects.filter(variant=variant,field__is_system=False,field__archived=False).select_related("field"):
        if machine_field_visibility(val.field, variant) and (val.text_value or val.file_value):
            custom_rows.append({"label":val.field.label,"text":val.text_value,"file":val.file_value})
    return render(request, "messen/machine_variant_detail.html", {
        "variant": variant, "product": variant.product, "application_rows": rows, "custom_rows":custom_rows, "field_visibility":visibility,
    })

@require_GET
def machine_series_compare(request, pk):
    from .models import MachineProduct, RecyclingArea
    product = get_object_or_404(MachineProduct, pk=pk, published=True)
    variants = list(product.variants.filter(published=True).prefetch_related("materials__area"))
    rows = []

    def add(label, values):
        values = [str(value).strip() if value else "—" for value in values]
        if any(value != "—" for value in values):
            rows.append({"label": label, "values": values,
                         "different": len(set(values)) > 1})

    for label, field in (("AUSFÜHRUNG", "version"), ("MOTOR", "engine"),
                         ("ANTRIEB / LEISTUNG", "drive"), ("GEWICHT", "weight")):
        add(label, [getattr(v, field) for v in variants])

    areas = list(RecyclingArea.objects.all())
    for area in areas:
        add(area.title.upper(), [", ".join(m.name for m in v.materials.all()
            if m.area_id == area.pk) for v in variants])

    # Legacy fields remain visible when an older machine was not yet migrated.
    for label, field in (("HOLZ (WEITERE ANGABEN)", "applications_wood"),
                         ("MÜLL (WEITERE ANGABEN)", "applications_waste"),
                         ("SONSTIGE EINSATZGEBIETE", "applications_other")):
        values = [getattr(v, field) for v in variants]
        if field in ("applications_wood", "applications_waste"):
            values = [value if not v.materials.all() else "" for value, v in zip(values, variants)]
        add(label, values)

    add("FUNKTIONSprinzip".upper(), [v.operating_principle for v in variants])
    add("BESCHREIBUNG", [v.description or product.description for v in variants])

    specs = []
    for v in variants:
        parsed = {}
        for line in v.additional_specs.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                key, value = key.strip(), value.strip()
            else:
                key, value = "WEITERE ANGABEN", line
            if key:
                parsed[key] = (parsed.get(key, "") + "; " + value).strip("; ")
                if key not in specs:
                    specs.append(key)
        v._comparison_specs = parsed
    for key in specs:
        add(key.upper(), [v._comparison_specs.get(key, "") for v in variants])
    add("DATENBLATT", [v.datasheet_url for v in variants])
    add("TECHNISCHE ZEICHNUNG", [v.technical_drawing.url if v.technical_drawing else v.technical_drawing_url for v in variants])
    from .models import MachineField, MachineFieldValue
    from .staff_views import machine_field_visibility
    definitions={f.key:f for f in MachineField.objects.filter(archived=False)}
    standard_labels={"version":"AUSFÜHRUNG","engine":"MOTOR","drive":"ANTRIEB / LEISTUNG","weight":"GEWICHT","operating_principle":"FUNKTIONSprinzip".upper(),"description":"BESCHREIBUNG","datasheet_url":"DATENBLATT","technical_drawing":"TECHNISCHE ZEICHNUNG"}
    reverse_labels={v:k for k,v in standard_labels.items()}
    filtered=[]
    for row in rows:
        key=reverse_labels.get(row["label"])
        if key and key in definitions:
            values=[value if machine_field_visibility(definitions[key],v,compare=True) else "—" for value,v in zip(row["values"],variants)]
            if all(value=="—" for value in values):continue
            row=dict(row,values=values,different=len(set(values))>1)
        elif row["label"] in [a.title.upper() for a in areas] and "materials" in definitions:
            values=[value if machine_field_visibility(definitions["materials"],v,compare=True) else "—" for value,v in zip(row["values"],variants)]
            if all(value=="—" for value in values):continue
            row=dict(row,values=values,different=len(set(values))>1)
        filtered.append(row)
    rows=filtered
    for field in MachineField.objects.filter(is_system=False,archived=False):
        values=[]
        for variant in variants:
            val=MachineFieldValue.objects.filter(field=field,variant=variant).first()
            value=(val.file_value.url if val and val.file_value else val.text_value if val else "")
            values.append(value if machine_field_visibility(field,variant,compare=True) else "")
        add(field.label.upper(),values)
    return render(request, "messen/machine_series_compare.html", {
        "product": product, "variants": variants, "comparison_rows": rows,
    })


@require_GET
def recycling_area_machines(request, slug):
    """Public data for linking LÖSUNGEN recycling categories to published variants."""
    from .models import RecyclingArea, MachineVariant
    area = get_object_or_404(RecyclingArea, slug=slug)
    variants = MachineVariant.objects.filter(
        published=True, product__published=True, materials__area=area
    ).select_related("product").distinct().order_by("product__model_name", "name")
    return JsonResponse({
        "area": area.title,
        "machines": [
            {"name": v.name, "series": v.product.model_name,
             "url": "/maschinen/variante/%s/" % v.pk}
            for v in variants
        ],
    })


@require_GET
def recycling_machines_overview(request):
    """Published machine variants grouped by actual RecyclingArea/Material associations."""
    from .models import RecyclingArea, MachineVariant
    areas = RecyclingArea.objects.prefetch_related("materials").all()
    result = []
    for area in areas:
        variants = (MachineVariant.objects.filter(
            published=True, product__published=True, materials__area=area
        ).select_related("product").distinct().order_by("product__model_name", "name"))
        result.append({"slug": area.slug, "title": area.title,
                       "machines": [{"name": x.name, "series": x.product.model_name,
                                     "category": x.product.category,
                                     "category_label": x.product.get_category_display(),
                                     "url": "/maschinen/variante/%s/" % x.pk} for x in variants]})
    return JsonResponse({"areas": result})
