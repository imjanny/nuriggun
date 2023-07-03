from django.test import TestCase
from weather.models import WeatherCity
from weather.views import load_weather, save_weather
import unittest
import datetime

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

        print("날씨데이터 get")

    def test_save_weather(self):

        save_weather()  

        print("날씨데이터 저장완료!")


if __name__ == '__main__':
    unittest.main()




