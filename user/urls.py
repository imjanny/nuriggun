from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView
from user.views import ConfirmEmailView
from django.urls import re_path

urlpatterns = [
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    # 여기까지 기본 회원가입 로그인
    re_path(
        r"^account-confirm-email/$",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    re_path(
        r"^account-confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    # 여기까지 이메일인증
]
