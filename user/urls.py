from django.urls import path
from user import views


urlpatterns = [
    path('', views.UserView.as_view(), name="user_view"),

    # HOME
    path("home/userlist/", views.HomeUserListView.as_view(), name="home_user_list_view"),

    # 회원가입(이메일인증)
    path('signup/', views.SignUpView.as_view(), name='sign_up_view'),
    path("verify-email/<str:uidb64>/<str:token>/",views.VerifyEmailView.as_view(), name='verify-email'),

    # 로그인
    path("login/", views.LoginView.as_view(), name="login_view"),

    # 비밀번호 재설정 URL
    path('password/reset/', views.PasswordResetView.as_view(), name='rest_password_reset_view'),
    path(
        "password/reset/check/<str:uidb64>/<str:token>/",
        views.PasswordTokenCheckView.as_view(),
        name="password_reset_confirm",
    ),  
    path("password/reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm_view"), 
    
    # 비밀번호 찾기 
    path("password/change/<int:user_id>/", views.PasswordChangeView.as_view(), name="password_change_view"),

    # /user/subscribe/<int:user_id>/ 구독
    path('subscribe/<int:user_id>/', views.SubscribeView.as_view(), name='subscribe_view'), 

    # 프로필
    path('profile/<int:user_id>/', views.UserView.as_view(), name='profile_view'),

    #소셜로그인 api
    path('kakao/login/', views.KakaoLoginView.as_view(), name='kakao_login'),

    # 쪽지
    path('messages/inbox/', views.MessageInboxView.as_view(), name='message_inbox'),
    path('messages/sent/', views.MessageSentView.as_view(), name='message_sent'),
    path('messages/create/', views.MessageView.as_view(), name='message_create'),
    path('messages/<int:message_id>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:message_id>/reply/', views.MessageReplyView.as_view(), name='message_reply'),

    # 신고
    path('report/<int:user_id>/report/', views.ReportView.as_view(), name='report_user'),

    # 이메일 알림 동의
    path('email/notification/', views.EmailNotificationView.as_view(), name='email_notification'),
    
]

