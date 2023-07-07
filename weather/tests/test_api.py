from django.test import TestCase
from weather.models import WeatherCity, WeatherData
from weather.views import load_weather, save_weather

class WeatherTestCase(TestCase):
    def setUp(self):
        Seoul = WeatherCity.objects.create(city = 'Seoul', nx = 60, ny = 127)
        self.nx = Seoul.nx
        self.ny = Seoul.ny

    def test_load_weather(self):

        weather_data = load_weather(self.nx, self.ny)

        self.assertIn('tmp', weather_data)
        self.assertIn('hum', weather_data)
        self.assertIn('sky', weather_data)
        self.assertIn('rain', weather_data)

    def test_save_weather(self):

        save_weather()  
        seoul_weather = WeatherData.objects.filter(city__city="Seoul").latest('timestamp')
        self.assertIsNotNone(seoul_weather.temp) 
        self.assertIsNotNone(seoul_weather.humidity) 
        self.assertIsNotNone(seoul_weather.rain) 
        self.assertIsNotNone(seoul_weather.sky)

