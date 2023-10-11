from django.apps import AppConfig
from controls.models import SystemConfig, StartupConfig
from controls.api_comms import ApiComms


class ControlsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'controls'

    def ready(self):
        api = ApiComms()
        if SystemConfig.objects.exists() and StartupConfig.objects.exists():
            api.configure()
