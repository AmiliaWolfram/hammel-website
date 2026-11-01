from django.apps import AppConfig
class MessenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "messen"

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.contrib.auth.models import Group, Permission
        def grant_vertrieb_permissions(sender, **kwargs):
            if sender.label != "messen":
                return
            group, _ = Group.objects.get_or_create(name="Vertrieb")
            permissions = Permission.objects.filter(
                content_type__app_label="messen",
                content_type__model__in=["machineproduct", "usedmachine", "usedmachinephoto"],
            )
            group.permissions.add(*permissions)
        post_migrate.connect(grant_vertrieb_permissions, sender=self, dispatch_uid="messen_vertrieb_permissions")
