from user.models import User

from rest_framework import serializers

from django.conf import settings


# 구독
class SubscribeSerializer(serializers.ModelSerializer):
    subscribe = serializers.SerializerMethodField()

    def get_subscribe(self, obj):
        subscribes = obj.subscribe.all()
        return [
            {
                "id": subscribes.id,
                "nickname": subscribes.nickname,
                "profile_image": self.get_profile_image_url(subscribes.profile_img),
            }
            for subscribes in subscribes
        ]

    def get_profile_image_url(self, profile_img):
        if profile_img:
            return f"{settings.MEDIA_URL}{profile_img}"
        return None

    class Meta:
        model = User
        fields = ["subscribe"]

class UserSerializer(serializers.ModelSerializer):
    '''유저 프로필 GET, PATCH, DELETE용 시리얼라이저'''
    class Meta:
        model = User
        fields = ('pk', 'email', 'nickname', 'interest', 'profile_img', 'subscribe')
        read_only_fields = ('email',)
