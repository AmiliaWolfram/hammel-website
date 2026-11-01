from django.core.exceptions import ValidationError
from django.db import models

class Messe(models.Model):
    title = models.CharField("Messename", max_length=180)
    start_date = models.DateField("Beginn")
    end_date = models.DateField("Ende")
    city = models.CharField("Stadt", max_length=100)
    country = models.CharField("Land", max_length=100, blank=True)
    booth = models.CharField("Halle / Stand", max_length=100, blank=True)
    description = models.TextField("Beschreibung", blank=True)
    url = models.URLField("Messe-Website", blank=True)
    image = models.ImageField("Messebild", upload_to="messen/", blank=True)
    published = models.BooleanField("Öffentlich sichtbar", default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_date", "title"]
        verbose_name = "Messe"
        verbose_name_plural = "Messen"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Das Ende darf nicht vor dem Beginn liegen."})

    def __str__(self):
        return self.title


class MessePhoto(models.Model):
    messe = models.ForeignKey(Messe, on_delete=models.CASCADE, related_name="photos", verbose_name="Messe")
    image = models.ImageField("Galeriefoto", upload_to="messen/gallery/")
    caption = models.CharField("Bildunterschrift", max_length=180, blank=True)
    position = models.PositiveIntegerField("Reihenfolge", default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Messefoto"
        verbose_name_plural = "Messefotos"


class NewsArticle(models.Model):
    CATEGORY_CHOICES = [("news", "News"), ("innovation", "Innovationen"), ("people", "Menschen"), ("insights", "Einblicke"), ("events", "Events")]
    title = models.CharField("Titel", max_length=220)
    teaser = models.TextField("Kurzbeschreibung", blank=True)
    body = models.TextField("Artikeltext", blank=True)
    category = models.CharField("Kategorie", max_length=20, choices=CATEGORY_CHOICES, default="news")
    published_at = models.DateField("Datum")
    image = models.ImageField("Titelbild", upload_to="news/", blank=True)
    external_url = models.URLField("Externer Link", blank=True)
    featured = models.BooleanField("Hauptstory", default=False)
    published = models.BooleanField("Veröffentlicht", default=False)
    class Meta:
        ordering = ["-published_at", "-id"]
        verbose_name = "Newsbeitrag"
        verbose_name_plural = "Newsverwaltung"
    def __str__(self):
        return self.title


class UsedMachine(models.Model):
    title = models.CharField("Maschinenbezeichnung", max_length=180)
    serial_number = models.CharField("Maschinennummer", max_length=70, blank=True)
    build_year = models.PositiveSmallIntegerField("Baujahr", null=True, blank=True)
    build_month = models.PositiveSmallIntegerField("Baumonat", null=True, blank=True, choices=[(i, str(i)) for i in range(1, 13)])
    operating_hours = models.CharField("Betriebsstunden", max_length=90, blank=True)
    engine = models.CharField("Motor", max_length=220, blank=True)
    power = models.CharField("Leistung", max_length=100, blank=True)
    shafts = models.TextField("Wellen / Werkzeuge", blank=True)
    equipment = models.TextField("Ausstattung", blank=True)
    condition = models.TextField("Zustand", blank=True)
    weight = models.CharField("Gewicht", max_length=100, blank=True)
    description = models.TextField("Beschreibung", blank=True)
    image = models.ImageField("Hauptbild", upload_to="used-machines/", blank=True)
    video_url = models.URLField("YouTube Video", blank=True)
    published = models.BooleanField("Auf Website sichtbar", default=False)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["position", "-id"]
        verbose_name = "Gebrauchtmaschine"
        verbose_name_plural = "Gebrauchtmaschinen"
    def __str__(self): return self.title

class UsedMachinePhoto(models.Model):
    machine = models.ForeignKey(UsedMachine, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField("Foto", upload_to="used-machines/gallery/")
    caption = models.CharField("Bildunterschrift", max_length=180, blank=True)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    class Meta:
        ordering = ["position", "id"]


class MachineProduct(models.Model):
    CATEGORIES = [("vorbrecher", "Vorbrecher"), ("nachzerkleinerer", "Nachzerkleinerer"), ("siebtechnik", "Siebtechnik"), ("sortiertechnik", "Sortiertechnik"), ("anlagenbau", "Anlagenbau")]
    category = models.CharField("Kategorie", max_length=30, choices=CATEGORIES)
    model_name = models.CharField("Modell", max_length=120, unique=True)
    headline = models.CharField("Kurzbeschreibung", max_length=240, blank=True)
    description = models.TextField("Beschreibung", blank=True)
    applications = models.TextField("Einsatzgebiete", blank=True)
    technical_data = models.TextField("Technische Daten (je Zeile)", blank=True)
    advantages = models.TextField("Vorteile (je Zeile)", blank=True)
    image = models.ImageField("Produktfoto", upload_to="machine-products/", blank=True)
    image_url = models.URLField("Bild-URL (optional)", blank=True)
    datasheet_url = models.URLField("Datenblatt-URL", blank=True)
    published = models.BooleanField("Öffentlich sichtbar", default=True)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["position", "model_name"]
        verbose_name = "Maschinenmodell"
        verbose_name_plural = "Maschinenkatalog"
    def __str__(self): return self.model_name


class MachineVariant(models.Model):
    """Editable technical profile for one physical model/version (D, DK, E)."""
    product = models.ForeignKey(MachineProduct, on_delete=models.CASCADE, related_name="variants", verbose_name="Baureihe")
    name = models.CharField("Modellversion", max_length=130, unique=True)
    version = models.CharField("Ausführung", max_length=120, blank=True)
    engine = models.CharField("Motor", max_length=240, blank=True)
    drive = models.CharField("Antrieb / Leistung", max_length=140, blank=True)
    weight = models.CharField("Gewicht", max_length=180, blank=True)
    applications_wood = models.TextField("Einsatzgebiet Holz", blank=True)
    applications_waste = models.TextField("Einsatzgebiet Müll", blank=True)
    applications_other = models.TextField("Weitere Einsatzgebiete", blank=True)
    materials = models.ManyToManyField("RecyclingMaterial", blank=True, related_name="machine_variants", verbose_name="Einsatzmaterialien")
    operating_principle = models.TextField("Funktionsprinzip", blank=True)
    description = models.TextField("Beschreibung", blank=True)
    additional_specs = models.TextField("Weitere technische Daten (eine Zeile: Merkmal: Wert)", blank=True)
    image = models.ImageField("Maschinenfoto", upload_to="machine-variants/", blank=True)
    image_url = models.URLField("Foto-URL", blank=True)
    datasheet_url = models.URLField("Datenblatt", blank=True)
    technical_drawing = models.FileField("Technische Zeichnung (PDF oder Bild)", upload_to="machine-variants/drawings/", blank=True)
    technical_drawing_url = models.URLField("Technische Zeichnung URL", blank=True)
    hero_media_choice = models.CharField("Hero-Darstellung", max_length=10, choices=(("auto", "Automatisch"), ("video", "Video"), ("image", "Foto")), default="auto")
    hero_video = models.FileField("Hero-Video (MP4/WebM)", upload_to="machine-variants/videos/", blank=True)
    hero_video_url = models.URLField("Hero-Video URL (MP4/WebM)", blank=True)
    published = models.BooleanField("Veröffentlicht", default=False)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    class Meta:
        ordering = ["position", "name"]
        verbose_name = "Maschinenvariante"
        verbose_name_plural = "Maschinenvarianten"
    def __str__(self): return self.name

# Centrally maintained recycling areas and their specific materials.
class RecyclingArea(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=180)
    position = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ("position", "pk")
        verbose_name = "Recyclingbereich"
        verbose_name_plural = "Recyclingbereiche"
    def __str__(self):
        return self.title

class RecyclingMaterial(models.Model):
    area = models.ForeignKey(RecyclingArea, related_name="materials", on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    position = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ("position", "pk")
        constraints = [models.UniqueConstraint(fields=("area", "name"), name="unique_recycling_material_per_area")]
    def __str__(self):
        return self.name


class MachineField(models.Model):
    """Editable field definition; standard fields are referenced by key."""
    FIELD_TYPES = [("text","Text"),("number","Zahl"),("boolean","Ja / Nein"),("url","URL"),("file","Datei / PDF"),("image","Bild"),("video","Video")]
    SECTIONS = [("general","Allgemeine Informationen"),("technical","Technische Daten"),("applications","Einsatzgebiete"),("media","Dokumente & Medien")]
    key = models.SlugField(max_length=100, unique=True)
    label = models.CharField(max_length=150)
    field_type = models.CharField(max_length=12, choices=FIELD_TYPES, default="text")
    section = models.CharField(max_length=20, choices=SECTIONS, default="technical")
    position = models.PositiveIntegerField(default=0)
    is_system = models.BooleanField(default=False)
    show_public = models.BooleanField(default=True)
    show_compare = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)
    class Meta:
        ordering = ("section", "position", "pk")
    def __str__(self): return self.label

class MachineFieldSetting(models.Model):
    """Override visibility at series or variant level; NULL inherits parent."""
    field = models.ForeignKey(MachineField, on_delete=models.CASCADE, related_name="settings")
    product = models.ForeignKey(MachineProduct, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(MachineVariant, on_delete=models.CASCADE, null=True, blank=True)
    show_public = models.BooleanField(null=True, blank=True)
    show_compare = models.BooleanField(null=True, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=("field", "product"), name="unique_series_field_setting"),models.UniqueConstraint(fields=("field", "variant"), name="unique_variant_field_setting")]

class MachineFieldValue(models.Model):
    field = models.ForeignKey(MachineField, on_delete=models.PROTECT, related_name="values")
    variant = models.ForeignKey(MachineVariant, on_delete=models.CASCADE, related_name="custom_values")
    text_value = models.TextField(blank=True)
    file_value = models.FileField(upload_to="machine-variants/extra/", blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=("field", "variant"), name="unique_machine_custom_value")]


class MachineVariantPhoto(models.Model):
    variant = models.ForeignKey(MachineVariant, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="machine-variants/gallery/")
    caption = models.CharField(max_length=180, blank=True)
    position = models.PositiveIntegerField(default=0)
    is_cover = models.BooleanField(default=False)
    class Meta:
        ordering = ("position", "pk")

class MachineVariantRevision(models.Model):
    variant = models.ForeignKey(MachineVariant, on_delete=models.CASCADE, related_name="revisions")
    author = models.ForeignKey("auth.User", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=30, default="saved")
    snapshot = models.JSONField(default=dict)
    class Meta:
        ordering = ("-created_at",)

class MachineVariantDraft(models.Model):
    variant = models.OneToOneField(MachineVariant, on_delete=models.CASCADE, related_name="editing_draft")
    author = models.ForeignKey("auth.User", null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    values = models.JSONField(default=dict)


class HomepageShowcase(models.Model):
    category = models.CharField("Kategorie", max_length=80, unique=True)
    product = models.ForeignKey("MachineProduct", null=True, blank=True, on_delete=models.SET_NULL, related_name="homepage_showcases")
    eyebrow = models.CharField("Oberzeile", max_length=120, blank=True)
    headline = models.CharField("Titel", max_length=160)
    description = models.CharField("Werbetext", max_length=300, blank=True)
    other_models = models.CharField("Weitere Modelle", max_length=300, blank=True)
    image = models.ImageField("Eigenes Bild", upload_to="homepage-showcase/", blank=True)
    image_path = models.CharField("Vorhandenes Bild (Pfad)", max_length=300, blank=True)
    button_text = models.CharField("Button-Text", max_length=120, blank=True)
    button_url = models.CharField("Button-Link", max_length=400, blank=True)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    is_default = models.BooleanField("Beim Laden zuerst anzeigen", default=False)
    published = models.BooleanField("Sichtbar", default=True)
    class Meta:
        ordering = ["position", "pk"]
    def __str__(self): return self.category
