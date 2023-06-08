from django.urls import path, include, re_path
from user import views
from dj_rest_auth.registration.views import VerifyEmailView
from user.views import ConfirmEmailView
# 비밀번호 재설정
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('', views.UserView.as_view(), name="user_view"),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    
    
    path('accounts/', include('allauth.urls')), # allauth의 기능을 accounts라는 주소 아래 담는다.
    ## 네이버 http://127.0.0.1:8000/accounts/naver/login/callback/

    # 비밀번호 재설정 URL
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # /user/subscribe/<int:user_id>/ 구독
    path('subscribe/<int:user_id>/', views.SubscribeView.as_view(), name='subscribe_view'), 

    # 프로필
    path('profile/<int:user_id>/', views.UserView.as_view(), name='profile_view'),

    # 이메일 인증 / 인증링크 클릭해서 사이트로 돌아오기
    re_path(r'^account-confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', views.ConfirmEmailView.as_view(), name='account_confirm_email'),
]

