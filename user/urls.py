from django.urls import path, include
from user import views

# 비밀번호 재설정
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('', views.UserView.as_view(), name="user_view"),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # 비밀번호 재설정 URL
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # /user/subscribe/<int:user_id>/ 구독
    path('subscribe/<int:user_id>/', views.SubscribeView.as_view(), name='subscribe_view'), 

    # 프로필
    path('profile/<int:user_id>/', views.UserView.as_view(), name='profile_view'),
    #소셜로그인 api
    path('kakao/login/', views.KakaoLoginView.as_view(), name='kakao_login'),
]

