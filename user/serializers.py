from django.contrib.auth import get_user_model

from user.models import User, EmailNotificationSettings
from article.models import Article
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from .models import Message
import threading
from django.core.mail import EmailMessage
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from rest_framework import exceptions

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
        
# =============== 프로필 ================
class ProfileArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article 
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    subscribe_count = serializers.SerializerMethodField()
    subscribe = serializers.StringRelatedField(many=True, required=False)

    def get_subscribe_count(self, obj):
        return obj.subscribe.count()

    '''유저 프로필 GET, PATCH, DELETE용 시리얼라이저'''
    # user_articles = ProfileArticleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'pk', 'email', 'nickname', 'interest', 'profile_img', 'subscribe', 'subscribe_count')
        read_only_fields = ('email',)

# =============== 이메일 비동기전송 ==============   
class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(
            subject = message["subject"],
            body = message["message"],
            to = [message["to_email"]],
        )
        EmailThread(email).start()

    @staticmethod
    def send_password_reset_email(user, reset_url):
        subject = "[Nurriggun]비밀번호 재설정 인증 링크입니다."
        message = f"비밀번호 재설정 링크: {reset_url}"
        to_email = user.email

        reset_message = {
            "subject": subject,
            "message": message,
            "to_email": to_email, 
        }
        Util.send_email(reset_message)

class EmailThread(threading.Thread):
    '''비동기전송 : 회원가입 시 이메일전송으로 인한 지연현상이 없어짐'''
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


# =============== 회원가입(이메일인증) ==============   
import re

class UserCreateSerializer(serializers.ModelSerializer):
    '''회원가입'''
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'required': '이메일을 입력해주세요.',
                    'blank': '이메일을 입력해주세요.',
                    'invalid': '잘못된 이메일 형식입니다.',
                }
            },
            'password': {
                'error_messages': {
                    'required': '비밀번호를 입력해주세요.',
                    'blank': '비밀번호를 입력해주세요.',
                }
            },
        }

    def validate_email(self, value):
        # 이메일 정규식 : @기호 필요 / 마침표 필요
        email_pattern = r'^[\w.-]+@[a-zA-Z.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, value):
            raise serializers.ValidationError(self.fields['email'].error_messages['invalid'],
                code='invalid_email')
        
        return value
    
        
    def validate_nickname(self, value):
        if len(value) > 8:
            raise serializers.ValidationError("닉네임은 8자 이하여야 합니다.")
        
        # 부적절한 닉네임 필터링
        blocked_words = ['욕설1', '욕설2', '욕설3']  # 부적절한 단어 목록
        
        for word in blocked_words:
            if re.search(r'\b{}\b'.format(re.escape(word)), value, re.IGNORECASE):
                raise serializers.ValidationError("닉네임에 부적절한 단어가 포함되어 있습니다.")
        
        return value
    
    def validate_password(self, value):
        # 비밀번호 정규식 : 8자 이상 / 숫자+영문 조합
        password_pattern = r'^(?=.*\d)(?=.*[a-zA-Z]).{8,}$'

        if not re.match(password_pattern, value):
            raise serializers.ValidationError("비밀번호는 8자 이상이여야 하며 영문과 숫자를 포함하여야 합니다.")
        
        return value
    
    def create(self, validated_data):
        user = super().create(validated_data)
        password = validated_data.get('password')
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
        token["profile_img"] = user.profile_img.url if user.profile_img else None
        return token
    
    def for_user(self, user):
        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
#=========== 비밀번호 재설정 ============

class PasswordResetSerializer(serializers.Serializer):
        email = serializers.EmailField()

        def validate(self, attrs):
            try:
                email = attrs.get("email")
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)

                reset_url = f"https://nuriggun.xyz/user/password/reset/check/{uidb64}/{token}/"
        
                Util.send_password_reset_email(user, reset_url)
                return attrs

            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"email": "잘못된 이메일입니다. 다시 입력해주세요."}
                )

class PasswordConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, error_messages={
        'required': '비밀번호를 입력해주세요.',
        'blank': '비밀번호를 입력해주세요.',
    })
    password2 = serializers.CharField(write_only=True, error_messages={
        'required': '비밀번호 확인을 입력해주세요.',
        'blank': '비밀번호 확인을 입력해주세요.',
    })
    token = serializers.CharField(max_length=100,write_only=True,)
    uidb64 = serializers.CharField(max_length=100,write_only=True,)

    class Meta:
        fields = ("password", "password2", "token", "uidb64")

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        token = attrs.get("token")
        uidb64 = attrs.get("uidb64")
        password_pattern = r'^(?=.*\d)(?=.*[a-zA-Z]).{8,}$'

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if PasswordResetTokenGenerator().check_token(user, token) == False:
                raise exceptions.AuthenticationFailed("토큰이 유효하지 않습니다.", 401)
            if password != password2:
                raise serializers.ValidationError(
                    detail={"password2": "비밀번호가 일치하지 않습니다."}
                )
            if not re.match(password_pattern, password):
                raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 하며, 숫자와 문자의 조합이어야 합니다.")
        
            user.set_password(password)
            user.save()

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(detail={"user": "존재하지 않는 회원입니다."})
        
#=========== 비밀번호 재설정 끝 ============    

# 비밀번호 찾기
class PasswordChangeSerializer(serializers.ModelSerializer):
    '''프로필페이지->비밀번호 찾기 시리얼라이저'''
    password = serializers.CharField(write_only=True, error_messages={
        'required': '비밀번호를 입력해주세요.',
        'blank': '비밀번호를 입력해주세요.',
    })
    password2 = serializers.CharField(write_only=True, error_messages={
        'required': '비밀번호 확인을 입력해주세요.',
        'blank': '비밀번호 확인을 입력해주세요.',
    })
    class Meta:
        model = User
        fields = ("password", "password2")

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        password_pattern = r'^(?=.*\d)(?=.*[a-zA-Z]).{8,}$'

        user_id = self.context['user_id']

        user = User.objects.get(id=user_id)

        if password != password2:
            raise serializers.ValidationError(
                detail={"password2": "비밀번호가 일치하지 않습니다."}
            )
        if not re.match(password_pattern, password):
            raise serializers.ValidationError("비밀번호는 최소 8자 이상이어야 하며, 숫자와 문자의 조합이어야 합니다.")
    
        user.set_password(password)
        user.save()

        return attrs

# 쪽지


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class MessageCreateSerializer(serializers.ModelSerializer):
    """쪽지 작성 시리얼라이저"""

    receiver_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Message
        fields = ['receiver_email', 'title', 'content', 'image']

    def create(self, validated_data):
        receiver_email = validated_data.pop('receiver_email')
        receiver = get_user_model().objects.get(email=receiver_email)
        validated_data['receiver'] = receiver
        message = Message.objects.create(**validated_data)
        return message


class MessageDetailSerializer(serializers.ModelSerializer):
    """쪽지 상세보기 시리얼라이저"""

    sender = serializers.EmailField(source="sender.email")
    receiver = serializers.EmailField(source="receiver.email")

    def get_sender(self, obj):
        return obj.sender.email

    def get_receiver(self, obj):
        return obj.receiver.email

    class Meta:
        model = Message
        fields = "__all__"
        
        
class KakaoLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    access_token = serializers.CharField(required=False)

# ============ HOME ==============
class HomeUserListSerializer(serializers.ModelSerializer):
    '''메인페이지 용 유저리스트 시리얼라이저'''
    class Meta:
        model = User
        fields = ['pk', 'email', 'nickname', 'subscribe', 'profile_img']


"""이메일 알림 동의 시리얼라이저"""
class EmailNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailNotificationSettings
        fields = "__all__"