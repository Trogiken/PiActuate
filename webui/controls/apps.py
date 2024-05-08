from django.apps import AppConfig


class ControlsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'controls'

    def ready(self):
        from controls.models import SystemConfig, StartupConfig
        from controls.api_comms import ApiComms
        
        api = ApiComms()

        if SystemConfig.objects.exists() and StartupConfig.objects.exists():
            api.configure()
