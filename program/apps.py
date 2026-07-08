from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ProgramConfig(AppConfig):
    name = 'program'

    def ready(self):
        from .admin import enforce_role_permissions
        post_migrate.connect(enforce_role_permissions, sender=self)

