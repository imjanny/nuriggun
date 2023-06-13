import os
import requests
from django.shortcuts import redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer


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

# 소셜 로그인 import
from allauth.socialaccount.models import SocialAccount,SocialToken, SocialApp
from rest_framework_simplejwt.tokens import RefreshToken


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


# 쪽지 관련 view

'''받은 쪽지함'''
class MessageInboxView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(receiver=user)


'''보낸 쪽지함'''
class MessageSentView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user)


class MessageDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    '''쪽지 보기'''
    def get(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)

    '''쪽지 삭제 하기'''
    def delete(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        if request.method == 'POST':
            message.delete()
            return Response({"message": "삭제 완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)


''' 쪽지 보내기 '''
@api_view(['POST'])
def message_create(request):
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 소셜 로그인

# 카카오 로그인
class KakaoLoginView(APIView):
    def post(self, request):
        try:
            # 인증 코드를 가져옴
            code = request.data.get("code")

            # 인증 코드를 사용하여 액세스 토큰을 얻기 위해 카카오 서버에 요청
            access_token = requests.post(
                "https://kauth.kakao.com/oauth/token", 
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": os.environ.get("KAKAO_REST_API_KEY"),
                    "redirect_uri": "http://127.0.0.1:5500/user/index.html",  # 카카오에 등록된 리다이렉트 URI
                    "code": code,
                },
            )
            # 응답에서 액세스 토큰 가져오기
            access_token = access_token.json().get("access_token")

            # 액세스 토큰을 사용하여 사용자 정보를 얻기 위해 카카오 서버에 요청
            user_data = requests.get( 
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            # 응답에서 사용자 데이터 가져오기
            user_data = user_data.json()

            # 사용자 이메일, 닉네임 가져오기
            kakao_email = user_data.get("kakao_account")["email"]
            kakao_nickname = user_data.get("properties")["nickname"]

            try:
                # 사용자 이메일을 사용하여 유저 필터링
                user = User.objects.get(email=kakao_email)
                social_user = SocialAccount.objects.filter(user=user).first()

                # 유저가 존재하고 소셜 로그인 사용자인 경우
                if social_user:
                    # 카카오가 아닌 경우 에러 메시지
                    if social_user.provider != "kakao":
                        return Response({"error": "카카오로 가입한 유저가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

                    # 유저를 활성화하고 저장
                    user.is_active = True
                    user.save()

                    # 토큰 생성 ,가져오기
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "nickname": kakao_nickname,
                        },
                        status=status.HTTP_200_OK
                    )

                # 유저가 존재하지만 소셜 로그인 사용자가 아닌 경우 에러 메시지
                if social_user is None:
                    return Response({"error": "이메일이 존재하지만 , 소셜유저가 아닙니다"}, status=status.HTTP_400_BAD_REQUEST)

            # 유저가 존재하지 않는 경우
            except User.DoesNotExist:
                # 신규 유저를 생성하고 비밀번호를 설정하지 않음
                new_user = User.objects.create(nickname=kakao_nickname, email=kakao_email)
                new_user.set_unusable_password()
                new_user.save()

                # 소셜 계정 생성
                new_social_account = SocialAccount.objects.create(provider="kakao", user=new_user)

                # allauth 의 SocialApp
                social_app = SocialApp.objects.get(provider="kakao")

                # 이것도 alluath 의 SocialToken을 사용해서 토큰 생성
                SocialToken.objects.create(app=social_app, account=new_social_account, token=access_token)

                # 신규 유저 생성
                refresh = RefreshToken.for_user(new_user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "nickname": kakao_nickname,
                    },
                    status=status.HTTP_200_OK
                )
        # 자세한 에러를 보기위한 코드(개발단계)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)