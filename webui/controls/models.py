from django.db import models
from .validators import excluded_pin

# import max and min
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class SystemConfig(models.Model):
    class OffState(models.TextChoices):
        POWER_ON = True, 'On'
        POWER_OFF = False, 'Off'

    board_mode = models.CharField(max_length=5, default='BCM', editable=False,
                                  help_text="This is the help text for board_mode")

    relay1 = models.IntegerField(default=26, validators=[MinValueValidator(0), MaxValueValidator(31), excluded_pin], verbose_name="Relay 1", help_text="This is the help text for relay1")
    relay2 = models.IntegerField(default=20, validators=[MinValueValidator(0), MaxValueValidator(31), excluded_pin], verbose_name="Relay 2", help_text="This is the help text for relay2")
    switch1 = models.IntegerField(default=6, validators=[MinValueValidator(0), MaxValueValidator(31), excluded_pin], verbose_name="Switch 1", help_text="This is the help text for switch1")
    switch2 = models.IntegerField(default=13, validators=[MinValueValidator(0), MaxValueValidator(31), excluded_pin], verbose_name="Switch 2", help_text="This is the help text for switch2")
    switch3 = models.IntegerField(default=19, validators=[MinValueValidator(0), MaxValueValidator(31), excluded_pin], verbose_name="Switch 3", help_text="This is the help text for switch3")
    switch4 = models.IntegerField(default=23, validators=[MinValueValidator(0), MaxValueValidator(31), excluded_pin], verbose_name="Switch 4", help_text="This is the help text for switch4")
    switch5 = models.IntegerField(default=24, validators=[MinValueValidator(0), MaxValueValidator(31), excluded_pin], verbose_name="Switch 5", help_text="This is the help text for switch5")
    off_state = models.CharField(max_length=5, choices=OffState.choices, default=OffState.POWER_ON, verbose_name="Off State", help_text="This is the help text for off_state")
    timezone = models.CharField(max_length=100, verbose_name="Timezone", help_text="This is the help text for timezone")
    longitude = models.DecimalField(default=0.0, max_digits=9, decimal_places=6, verbose_name="Longitude", help_text="This is the help text for longitude")
    latitude = models.DecimalField(default=0.0, max_digits=9, decimal_places=6, verbose_name="Latitude", help_text="This is the help text for latitude")
    travel_time = models.IntegerField(default=10, verbose_name="Travel Time", help_text="This is the help text for travel_time")

    def __str__(self):
        return "SystemConfig"

    def save(self, *args, **kwargs):
        if not self.pk and SystemConfig.objects.exists():
            raise PermissionError('There can only be 1 SystemConfig instance')
        return super(SystemConfig, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "System Config"
        verbose_name_plural = "System Configs"


class StartupConfig(models.Model):
    # property function to give sunrise and sunset time?

    automation = models.BooleanField(default=False, verbose_name="Automation", help_text="Toggle automation on or off")
    auxillary = models.BooleanField(default=False, verbose_name="Auxillary", help_text="Toggle auxillary on or off")
    sunrise_offset = models.IntegerField(default=0, verbose_name="Sunrise Offset", help_text="Add or subtract minutes from sunrise")
    sunset_offset = models.IntegerField(default=0, verbose_name="Sunset Offset", help_text="Add or subtract minutes from sunset")

    def __str__(self):
        return "StartupConfig"

    def save(self, *args, **kwargs):
        if not self.pk and StartupConfig.objects.exists():
            raise PermissionError('There can only be 1 StartupConfig instance')
        return super(StartupConfig, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Startup Config"
        verbose_name_plural = "Startup Configs"