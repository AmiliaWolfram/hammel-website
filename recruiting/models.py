from django.db import models
from django.utils.text import slugify

class Vacancy(models.Model):
    CATEGORY = [("job", "Stellenangebot"), ("ausbildung", "Ausbildung"), ("praktikum", "Praktikum"), ("werkstudent", "Werkstudent")]
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=210, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY, default="job")
    location = models.CharField(max_length=120, default="Bad Salzungen")
    employment_type = models.CharField(max_length=120, blank=True)
    introduction = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True, help_text="Eine Aufgabe pro Zeile")
    requirements = models.TextField(blank=True, help_text="Eine Anforderung pro Zeile")
    benefits = models.TextField(blank=True, help_text="Ein Vorteil pro Zeile")
    published = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "stelle"
            slug = base
            i = 2
            while Vacancy.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"; i += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self): return self.title
    class Meta: ordering = ["sort_order", "-created_at"]

class Application(models.Model):
    STATUS = [("new", "Neu"), ("review", "In Prüfung"), ("interview", "Gespräch"), ("declined", "Abgesagt"), ("accepted", "Zusage")]
    vacancy = models.ForeignKey(Vacancy, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=60, blank=True)
    department = models.CharField(max_length=120, blank=True)
    available_from = models.CharField(max_length=100, blank=True)
    motivation = models.TextField()
    cv = models.FileField(upload_to="hr/cv/%Y/%m/")
    cover_letter = models.FileField(upload_to="hr/cover/%Y/%m/", blank=True)
    certificates = models.FileField(upload_to="hr/certificates/%Y/%m/", blank=True)
    privacy_consent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default="new")
    notes = models.TextField(blank=True, help_text="Nur für HR")
    created_at = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)
    def __str__(self): return f"{self.full_name} ({self.created_at:%d.%m.%Y})"
    class Meta: ordering = ["-created_at"]

class HRTip(models.Model):
    title = models.CharField(max_length=140)
    body = models.TextField()
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)
    class Meta: ordering = ["order", "id"]
    def __str__(self): return self.title


class ApplicationDepartment(models.Model):
    """Von HR gepflegte Auswahl für Initiativbewerbungen."""
    name = models.CharField(max_length=120, unique=True, verbose_name="Bereich")
    active = models.BooleanField(default=True, verbose_name="In der Bewerbung anzeigen")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Reihenfolge")

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Bewerbungsbereich"
        verbose_name_plural = "Bewerbungsbereiche"

    def __str__(self):
        return self.name


class ApplicationCertificate(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="certificate_files")
    file = models.FileField(upload_to="hr/certificates/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Zeugnis oder Zertifikat"
        verbose_name_plural = "Zeugnisse und Zertifikate"

    def __str__(self):
        return self.file.name.rsplit("/", 1)[-1]
