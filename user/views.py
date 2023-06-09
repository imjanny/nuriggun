import os
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404


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
        '''회원탈퇴 (계정 비활성화)'''
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
    
