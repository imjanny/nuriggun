from user.models import User

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings

import threading

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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

# =============== 회원가입(이메일인증) ==============   
 
class EmailThread(threading.Thread):
    '''비동기전송 : 회원가입 시 이메일전송으로 인한 지연현상이 없어짐'''
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class UserCreateSerializer(serializers.ModelSerializer):
    '''회원가입'''
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

# 로그인
class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["nickname"] = user.nickname
        return token