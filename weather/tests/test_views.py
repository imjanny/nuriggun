from rest_framework.test import APITestCase, APIClient
from weather.models import WeatherCity, WeatherData
from django.urls import reverse

class WeatherViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.city1 = WeatherCity.objects.create(city="서울", nx=60, ny=127)
        self.city2 = WeatherCity.objects.create(city="세종", nx=66, ny=103)

        self.weather1 = WeatherData.objects.create(city=self.city1, temp=31, humidity=57, rain=5, sky=1)
        self.weather2 = WeatherData.objects.create(city=self.city2, temp=27, humidity=80, rain=20, sky=3)
        self.weather3 = WeatherData.objects.create(city=self.city1, temp=31, humidity=57, rain=5, sky=1)

    def test_weather_view(self):
        url = reverse('weather_view')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

class WeatherViewNoDataTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_weather_view_no_data(self):
        url = reverse('weather_view')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

# 테스트 실행 명령어
# python manage.py test weather.tests.test_views -v 3
