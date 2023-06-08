import os
import requests
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponseRedirect, JsonResponse
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.github import views as github_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from .models import User

from user.serializers import (
    SubscribeSerializer,
    UserSerializer,
)

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
        '''회원탈퇴 (=계정 비활성화)'''
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            user.is_active = False
            user.save()
            return Response({"message": "탈퇴완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "탈퇴권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST) 
        
# 이메일인증 view
class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        return HttpResponseRedirect("http://127.0.0.1:5500/login.html")  # 인증성공

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                return HttpResponseRedirect("http://127.0.0.1:5500/login.html")  # 인증실패
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs


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
    
# ----- 구독 끝 -----

# 소셜 로그인

# 카카오 로그인
KAKAO_CALLBACK_URI = 'http://127.0.0.1:8000/user/kakao/callback/'

def kakao_login(request):
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email")

# 카카오 콜백
def kakao_callback(request):
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    code = request.GET.get("code")

    # code로 access token 요청
    token_request = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
    token_response_json = token_request.json()

    # 에러 발생 시 중단
    #json 내에 error 라는게 none이거나 아니면 실행, 오류 
    error = token_response_json.get("error", None)
    if error is not None:
        return JsonResponse({"error": "에러발생"}, status=400)
    # JsonResponse는 response를 커스터마이징 하여 전달하고 싶을때, http status code에 더하여 메세지를 입력해서 전달할 수 있다.

    access_token = token_response_json.get("access_token")
    
    # access token으로 카카오톡 프로필 요청
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None) # 이메일!

    if email is None:
        return JsonResponse({"error": "이메일이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != 'kakao':
            return JsonResponse({'error': '카카오유저가 아님'}, status=status.HTTP_400_BAD_REQUEST)
        
        #로그인이 잘 됏다는 리스폰
        return JsonResponse({"success": "로그인성공"}, status=200)

    except User.DoesNotExist:
    # 유저 아이디 생성
        new_user = User.objects.create_user(email=email, password=None,)
        new_user.save()
    
        # 여기서 새로운 소셜 계정을 생성하고 저장하고, 새로운 사용자와 연결해야 합니다.
        new_social_account = SocialAccount(user=new_user, provider="kakao", uid="...")
        new_social_account.save()

        return JsonResponse({"success": "사용자가 성공적으로 등록되었습니다"}, status=200)

    except SocialAccount.DoesNotExist:
        return JsonResponse({'error': '이메일이 소셜이메일이 아님'}, status=status.HTTP_400_BAD_REQUEST)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/user/kakao/callback/'
    client_class = OAuth2Client
    

## 깃허브 로그인

def github_login(request):
    client_id = os.environ.get("GITHUB_CLIENT_KEY")
    GITHUB_CALLBACK_URI = "http://127.0.0.1:8000/user/github/callback"
    return redirect(f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={GITHUB_CALLBACK_URI}&scope=read:user")


class GithubException(Exception):
    pass

def github_callback(request):
    client_id = os.environ.get("GITHUB_CLIENT_KEY")
    client_secret = os.environ.get("GIT_HUB_SECRET_KEY")
    code = request.GET.get("code")

    # code로 access token 요청
    token_request = requests.get(f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}")
    token_response_json = token_request.json()

    # 에러 발생 시 중단
    #json 내에 error 라는게 none이거나 아니면 실행, 오류 
    error = token_response_json.get("error", None)
    if error is not None:
        return JsonResponse({"error": "에러발생"}, status=400)
    # JsonResponse는 response를 커스터마이징 하여 전달하고 싶을때, http status code에 더하여 메세지를 입력해서 전달할 수 있다.

    access_token = token_response_json.get("access_token")
    
    # access token으로 깃허브 프로필 요청
    profile_request = requests.post(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    
    github_account = profile_json.get("github_account")
    email = github_account.get("email", None) # 이메일!

    if email is None:
        raise GithubException()
        
    try:
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != 'github':
            raise GithubException()
        
        #로그인이 잘 됏다는 리스폰
        return redirect({"success": "로그인성공"}, status=200)

    except User.DoesNotExist:
    # 유저 아이디 생성
        new_user = User.objects.create_user(email=email, password=None,)
        new_user.save()
    
        # 여기서 새로운 소셜 계정을 생성하고 저장하고, 새로운 사용자와 연결해야 합니다.
        new_social_account = SocialAccount(user=new_user, provider="github", uid="...")
        new_social_account.save()

        return JsonResponse({"success": "사용자가 성공적으로 등록되었습니다"}, status=200)

    except SocialAccount.DoesNotExist:
        raise GithubException()
    
    
class GithubLogin(SocialLoginView):
    adapter_class = github_view.OAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/user/github/callback/'
    client_class = OAuth2Client
    