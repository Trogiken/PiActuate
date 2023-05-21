from django.test import TestCase
from controls.models import StartupConfig, SystemConfig


class StartupConfigTestCase(TestCase):
    def setUp(self):
        StartupConfig.objects.create(automation='True', auxillary='True', sunrise_offset='0', sunset_offset='0')
    
    def test_startup_config(self):
        startup_config = StartupConfig.objects.first()
        self.assertEqual(startup_config.auxillary, True)
        self.assertEqual(startup_config.sunrise_offset, 0)
        self.assertEqual(startup_config.sunset_offset, 0)


class SystemConfigTestCase(TestCase):
    def setUp(self):
        SystemConfig.objects.create(board_mode='BCM', relay1='26', relay2='20', switch1='6', switch2='13', switch3='19', switch4='23', switch5='24', off_state='True', timezone='America/New_York', longitude='0.0', latitude='0.0', travel_time='10')
    
    def test_system_config(self):
        system_config = SystemConfig.objects.first()
        self.assertEqual(system_config.relay1, 26)
        self.assertEqual(system_config.relay2, 20)
        self.assertEqual(system_config.switch1, 6)
        self.assertEqual(system_config.switch2, 13)
        self.assertEqual(system_config.switch3, 19)
        self.assertEqual(system_config.switch4, 23)
        self.assertEqual(system_config.switch5, 24)
        self.assertEqual(system_config.off_state, True)
        self.assertEqual(system_config.timezone, 'America/New_York')
        self.assertEqual(system_config.longitude, 0.0)
        self.assertEqual(system_config.latitude, 0.0)
        self.assertEqual(system_config.travel_time, 10)
