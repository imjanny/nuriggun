from rest_framework import serializers
from .models import WeatherCity, WeatherData

class WeatherCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherCity
        fields = '__all__'


class WeatherDataSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='city.city')
    
    class Meta:
        model = WeatherData
        fields = '__all__'