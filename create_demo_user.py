
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()

username = os.environ["DEMO_USERNAME"]
password = os.environ["DEMO_PASSWORD"]

user, created = User.objects.get_or_create(
    username=username,
    defaults={"is_staff": True},
)

user.is_active = True
user.is_staff = True
user.is_superuser = False
user.set_password(password)
user.save()

# Demo access: view permissions only
view_permissions = Permission.objects.filter(
    content_type__app_label__in=[
        "messen",
        "contacts",
        "partners",
    ],
    codename__startswith="view_",
)

user.user_permissions.set(view_permissions)

print(
    f"Demo user '{username}' is ready "
    f"with {view_permissions.count()} view permissions."
)
