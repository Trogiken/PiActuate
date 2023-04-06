from django.db import models

# Create your models here.


class SystemConfig(models.Model):
    first_login = models.BooleanField(default=False)

    relay1 = models.IntegerField(default=26, max_length=2, help_text="This is the help text for relay1")
    relay2 = models.IntegerField(default=20, max_length=2, help_text="This is the help text for relay2")
    switch1 = models.IntegerField(default=6, max_length=2, help_text="This is the help text for switch1")
    switch2 = models.IntegerField(default=13, max_length=2, help_text="This is the help text for switch2")
    switch3 = models.IntegerField(default=19, max_length=2, help_text="This is the help text for switch3")
    switch4 = models.IntegerField(default=23, max_length=2, help_text="This is the help text for switch4")
    switch5 = models.IntegerField(default=24, max_length=2, help_text="This is the help text for switch5")
    board_mode = models.CharField(max_length=5, default='BCM', help_text="This is the help text for board_mode")
    off_state = models.BooleanField(default=True, help_text="This is the help text for off_state")
    timezone = models.CharField(max_length=100, default='US/Eastern', help_text="This is the help text for timezone")
    longitude = models.FloatField(default=-0.0, help_text="This is the help text for longitude")
    latitude = models.FloatField(default=0.0, help_text="This is the help text for latitude")
    travel_time = models.IntegerField(default=10, help_text="This is the help text for travel_time")

    def __str__(self):
        return "StartupConfig"

    def save(self, *args, **kwargs):
        if not self.pk and SystemConfig.objects.exists():
            raise PermissionError('There can only be 1 SystemConfig instance')
        return super(SystemConfig, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Startup Config"
        verbose_name_plural = "Startup Configs"


class StartupConfig(models.Model):
    # property function to give sunrise and sunset time?

    automation = models.BooleanField(default=False)
    sunrise_offset = models.IntegerField(default=0)
    sunset_offset = models.IntegerField(default=0)
