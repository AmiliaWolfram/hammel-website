from django.db import models

class ContactGroup(models.Model):
    name = models.CharField("Gruppenname", max_length=100, unique=True)
    sort_order = models.PositiveIntegerField("Reihenfolge", default=100)
    published = models.BooleanField("Auf Website anzeigen", default=True)
    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Kontaktgruppe"
        verbose_name_plural = "Kontaktgruppen"
    def __str__(self):
        return self.name

class ContactPerson(models.Model):
    name = models.CharField("Name", max_length=180)
    group = models.ForeignKey(ContactGroup, verbose_name="Gruppe", on_delete=models.PROTECT, related_name="people", null=True, blank=True)
    role = models.CharField("Funktion", max_length=255, blank=True)
    region = models.TextField("Zuständigkeitsbereich", blank=True)
    phone = models.TextField("Telefonnummern (eine pro Zeile)", blank=True)
    email = models.EmailField("E-Mail", blank=True)
    sort_order = models.PositiveIntegerField("Reihenfolge", default=100)
    published = models.BooleanField("Auf Website anzeigen", default=True)
    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Ansprechpartner"
        verbose_name_plural = "Ansprechpartner"
    def __str__(self):
        return self.name
