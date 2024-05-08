from django.contrib import admin

from .models import SystemConfig, StartupConfig

# Register your models here.

admin.site.register(SystemConfig)
admin.site.register(StartupConfig)