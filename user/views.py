from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404


from .models import User

from user.serializers import (
    SubscribeSerializer,
    UserSerializer,
    UserCreateSerializer,
    EmailThread,
    UserTokenObtainPairSerializer,
)

# 이메일 인증 import
from base64 import urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import redirect
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes

# 로그인 import
from rest_framework_simplejwt.views import TokenObtainPairView

# ============회원가입=============
class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(
            subject=message["email_subject"],
            body=message["email_body"],
            to=[message["to_email"]],
        )
        EmailThread(email).start()

class SignUpView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            uid = urlsafe_b64encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            email = user.email
            auth_url = f"http://localhost:8000/user/verify-email/{uid}/{token}/"
            
            email_body = "이메일 인증" + auth_url
            message = {
                "email_body": email_body,
                "to_email": email,
                "email_subject": "[Nurriggun] 회원가입 인증 이메일입니다.",
            }
            Util.send_email(message)

            return Response({"message": "가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        token_generator = PasswordResetTokenGenerator()

        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect("http://127.0.0.1:5500/user/login.html")
        else:
            return redirect("/")

# 로그인
class LoginView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

# ========= 프로필 ===========
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, user_id):
        '''프로필 보기'''
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def patch(self, request, user_id):
        '''프로필 수정하기'''
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "수정권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
    def delete(self,request, user_id):
        '''회원탈퇴 (계정 비활성화)'''
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            user.is_active = False
            user.save()
            return Response({"message": "탈퇴완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "탈퇴권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST) 
        

# ----- 구독 시작 -----

class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 구독 등록/취소
    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if you != me:
            if me in you.subscribes.all():
                you.subscribes.remove(me)
                return Response("구독 취소", status=status.HTTP_205_RESET_CONTENT)
            else:
                you.subscribes.add(me)
                return Response("구독 완료", status=status.HTTP_200_OK)
        else:
            return Response("자신을 구독 할 수 없습니다.", status=status.HTTP_403_FORBIDDEN)

    # 구독 리스트
    def get(self, request, user_id):
        subscribes = User.objects.filter(id=user_id)
        subscribes_serializer = SubscribeSerializer(subscribes, many=True)
        return Response(
            {
                "subscribe": subscribes_serializer.data
            }
        )
    
