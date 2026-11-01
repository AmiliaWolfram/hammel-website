from django.db import models
class Partner(models.Model):
    REGIONS=[("e","Europa"),("a","Asien"),("f","Afrika"),("n","Nordamerika"),("s","Südamerika"),("o","Ozeanien")]
    name=models.CharField("Unternehmen",max_length=200)
    country=models.CharField("Land / Vertriebsgebiet",max_length=120)
    city=models.CharField("Stadt",max_length=150,blank=True)
    address=models.TextField("Adresse",blank=True)
    phone=models.CharField("Telefon",max_length=120,blank=True)
    email=models.EmailField("E-Mail",blank=True)
    domain=models.CharField("Website",max_length=250,blank=True)
    description=models.TextField("Beschreibung",blank=True)
    eyebrow=models.CharField("Kurzzeile",max_length=300,blank=True)
    specialties=models.JSONField("Schwerpunkte",default=list,blank=True)
    source_url=models.URLField("Quelle",max_length=600,blank=True)
    theme=models.CharField("Designvariante",max_length=40,blank=True)
    tagline=models.CharField("Markenclaim",max_length=250,blank=True)
    brand_color=models.CharField("Akzentfarbe",max_length=7,blank=True)
    hero_image=models.URLField("Titelbild-URL",max_length=700,blank=True)
    official_logo=models.URLField("Offizielles Markenlogo",max_length=700,blank=True)
    region=models.CharField("Kontinent",max_length=1,choices=REGIONS,default="e")
    latitude=models.FloatField("Breitengrad",default=0)
    longitude=models.FloatField("Längengrad",default=0)
    logo=models.ImageField("Logo hochladen",upload_to="partners/logos/",blank=True)
    logo_url=models.URLField("Vorhandene Logo-URL",max_length=500,blank=True)
    sort_order=models.PositiveIntegerField("Reihenfolge",default=100)
    published=models.BooleanField("Online",default=True)
    class Meta:
        ordering=["sort_order","id"]
    def __str__(self):return f"{self.name} ({self.country})"
