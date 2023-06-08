from django.urls import path, include, re_path
from user import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.UserView.as_view(), name="user_view"),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('kakao/login/',views.kakao_login),
    path('kakao/callback/', views.kakao_callback),
    path('kakao/login/finish/', views.KakaoLogin.as_view(), name='google_login_todjango'),
    
]