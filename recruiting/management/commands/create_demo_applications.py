"""Create clearly marked demo applications, without emailing anyone."""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from recruiting.models import Application, Vacancy

def sample_pdf(label):
    # Minimal, valid single-page PDF without additional dependencies.
    safe = label.encode("ascii", "replace").decode("ascii").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 18 Tf 50 760 Td ({safe}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\\nstream\\n" + stream + b"\\nendstream",
    ]
    data = bytearray(b"%PDF-1.4\\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\\n".encode() + obj + b"\\nendobj\\n")
    start = len(data)
    data.extend(b"xref\\n0 6\\n0000000000 65535 f \\n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \\n".encode())
    data.extend(b"trailer\\n<< /Size 6 /Root 1 0 R >>\\nstartxref\\n" + str(start).encode() + b"\\n%%EOF")
    return bytes(data)

class Command(BaseCommand):
    help = "Create demo Bewerbungen (idempotent, no emails)."

    def handle(self, *args, **kwargs):
        demos = [
            ("TEST – Lena Beispiel", "test-lena@example.invalid", "Verwaltung",
             "Ich bewerbe mich fuer eine kaufmaennische Stelle und freue mich auf ein Gespraech.", "review"),
            ("TEST – Max Muster", "test-max@example.invalid", "Service",
             "Ich habe Erfahrung mit technischen Anlagen und moechte das Serviceteam unterstuetzen.", "review"),
            ("TEST – Sofia Demo", "test-sofia@example.invalid", "Vertrieb",
             "Ich interessiere mich fuer die Kundenbetreuung und den internationalen Vertrieb.", "review"),
            ("TEST – Jonas Probe", "test-jonas@example.invalid", "Logistik",
             "Ich moechte meine Erfahrung in Lager und Versand bei HAMMEL einbringen.", "review"),
            ("TEST – Mia Beispiel", "test-mia@example.invalid", "Ausbildung",
             "Ich interessiere mich fuer eine Ausbildung und moechte mich vorstellen.", "new"),
        ]
        vacancies = list(Vacancy.objects.order_by("id"))
        for i, (name, email, department, motivation, status) in enumerate(demos):
            vacancy = (vacancies[i % len(vacancies)] if vacancies else None)
            app, created = Application.objects.get_or_create(
                email=email,
                defaults=dict(full_name=name, vacancy=vacancy, department=department,
                              available_from="Ab sofort", motivation=motivation,
                              privacy_consent=True, status=status,
                              notes="TESTDATENSATZ – keine echte Bewerbung.",
                              notification_sent=False),
            )
            if created:
                app.cv.save(f"TEST_Lebenslauf_{i+1}.pdf",
                            ContentFile(sample_pdf(f"TEST Lebenslauf {name}")), save=False)
                app.cover_letter.save(f"TEST_Anschreiben_{i+1}.pdf",
                                      ContentFile(sample_pdf(f"TEST Anschreiben {name}")), save=False)
                app.save()
                self.stdout.write(self.style.SUCCESS(f"Angelegt: {name} (#{app.pk})"))
            else:
                self.stdout.write(f"Bereits vorhanden: {name} (#{app.pk})")
        self.stdout.write("Keine E-Mails versendet.")
