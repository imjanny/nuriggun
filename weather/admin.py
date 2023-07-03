from django.contrib import admin
from weather.models import WeatherCity, WeatherData

admin.site.register(WeatherCity)
admin.site.register(WeatherData)
