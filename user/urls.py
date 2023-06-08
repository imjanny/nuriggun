from django.urls import path, include, re_path
from user import views
<<<<<<< HEAD
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
=======
from dj_rest_auth.registration.views import VerifyEmailView
from user.views import ConfirmEmailView
# 비밀번호 재설정
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
>>>>>>> origin/dev

urlpatterns = [
    path('', views.UserView.as_view(), name="user_view"),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('kakao/login/',views.kakao_login),
    path('kakao/callback/', views.kakao_callback),
    path('kakao/login/finish/', views.KakaoLogin.as_view(), name='google_login_todjango'),
    
<<<<<<< HEAD
]
=======
    path('accounts/', include('allauth.urls')), # allauth의 기능을 accounts라는 주소 아래 담는다.
    ## 네이버 http://127.0.0.1:8000/accounts/naver/login/callback/

    # 이메일인증 (없어도 되지만 일단 주석처리 해두겠습니다...)
    # re_path(r"^account-confirm-email/$", VerifyEmailView.as_view(), name="account_email_verification_sent",),
    # re_path(r"^account-confirm-email/(?P<key>[-:\w]+)/$", ConfirmEmailView.as_view(), name="account_confirm_email",),

    # 비밀번호 재설정 URL
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    

    path('subscribe/<int:user_id>/', views.SubscribeView.as_view(), name='subscribe_view'), # /user/subscribe/<int:user_id>/ 구독
]

>>>>>>> origin/dev
