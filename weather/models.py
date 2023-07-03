from django.db import models
from django.utils import timezone

class WeatherCity(models.Model):
    city = models.CharField(max_length=50, blank=True, null=True)
    nx = models.IntegerField(blank=True, null=True) # 격자 x
    ny = models.IntegerField(blank=True, null=True) # 격자 y 

    def __str__(self):
        return self.city
    
class WeatherData(models.Model):
    city = models.ForeignKey(WeatherCity, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True, null=True, blank=True) # 시간
    temp = models.FloatField(blank=True, null=True) # 온도
    humidity = models.IntegerField(blank=True, null=True) # 습도
    rain = models.CharField(max_length=20, blank=True, null=True) # 한시간 강수량
    sky = models.IntegerField(blank=True, null=True) # 하늘 상태

    def __str__(self):
        korea_timestamp = timezone.localtime(self.timestamp)

        city_name = self.city.city if self.city else "Unknown City"

        return f"{city_name} : {korea_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"