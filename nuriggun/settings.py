from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import my_settings
from corsheaders.defaults import default_methods




FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 이미지 크기 10MB까지

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(PROJECT_DIR, '.env'))

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'user',
    'article',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',
]

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (

        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )

}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nuriggun.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nuriggun.wsgi.application'

DATABASES = my_settings.DATABASES



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = 'static/'

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1:5500',
    'http://localhost:5500',
    'https://teamnuri.xyz',
]

CSRF_TRUSTED_ORIGINS=CORS_ALLOWED_ORIGINS


CORS_ALLOW_METHODS = list(default_methods) + [
    "",
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5000),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('SECRET_KEY'),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",

}

AUTHENTICATION_BACKENDS = [ # 소셜로그인 
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 사이트 1개만 사용
SITE_ID = 1

# REST_USE_JWT = True

AUTH_USER_MODEL = 'user.User'
# 소셜로그인부분 ! 
ACCOUNT_UNIQUE_EMAIL = True # 이메일을 유니크로 쓸것인지
ACCOUNT_USER_MODEL_USERNAME_FIELD = None #유저 네임 필드가 없어도 됨
ACCOUNT_USERNAME_REQUIRED = False # 아이디로 로그인 하지않고 
ACCOUNT_EMAIL_REQUIRED = True # 이메일로 로그인하게 만듦
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = 'https://teamnuri.xyz/user/kakaocode.html/' # 로그인되면 리다이렉트 될 페이지 프론트로 해야겠죠 ? 만들면 주석풀기 ~
ACCOUNT_LOGOUT_REDIRECT_URL = '/' #이건 로그아웃 로그아웃 요청은 /accounts/logout 여기임! 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' # 메일 호스트 서버
EMAIL_PORT = '587' # naver와 통신하는 포트
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER") # 발신할 이메일
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD") # 발신할 메일의 비밀번호
EMAIL_USE_TLS = True # TLS 보안 방법
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


#소셜 로그인 관련
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',    
    'allauth.account.auth_backends.AuthenticationBackend',
]