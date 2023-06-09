from django.urls import path, include
from user import views
# 비밀번호 재설정
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('', views.UserView.as_view(), name="user_view"),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # 이메일인증 다른방법
    path('signup/', views.SignUpView.as_view(), name='sign_up_view'), # /user/signup/
    path("verify-email/b'<str:uidb64>'/<str:token>/",views.VerifyEmailView.as_view(), name='verify-email'),

    # 로그인
    path("login/", views.LoginView.as_view(), name="login_view"),

    path('accounts/', include('allauth.urls')), # allauth의 기능을 accounts라는 주소 아래 담는다.
    ## 네이버 http://127.0.0.1:8000/accounts/naver/login/callback/

    # 비밀번호 재설정 URL
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # /user/subscribe/<int:user_id>/ 구독
    path('subscribe/<int:user_id>/', views.SubscribeView.as_view(), name='subscribe_view'), 

    # 프로필
    path('profile/<int:user_id>/', views.UserView.as_view(), name='profile_view'),
]

