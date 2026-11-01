
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ["DEMO_USERNAME"]
password = os.environ["DEMO_PASSWORD"]

user, created = User.objects.get_or_create(
    username=username,
    defaults={"is_staff": True}
)

user.is_staff = True
user.set_password(password)
user.save()

print("Demo user is ready")
