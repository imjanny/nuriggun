from rest_framework.test import APITestCase, override_settings
from django.urls import reverse
from user.models import User
from django.core import mail
import asyncio
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from base64 import urlsafe_b64encode
from django.utils.encoding import force_bytes


# 회원가입 TEST
class SignUpViewTest(APITestCase):
    '''비밀번호 유효성 검사'''
    def test_signup_1(self):
        url = reverse("sign_up_view")
        data = {
            "email" : "test@test.test",
            "password": "123456"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    '''비밀번호 빈값'''
    def test_signup_2(self):
        url = reverse("sign_up_view")
        data = {
            "email" : "test@test.test"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    '''이메일 빈값'''
    def test_signup_3(self):
        url = reverse("sign_up_view")
        data = {
            "password": "123456"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    '''이메일/비밀번호 빈값'''
    def test_signup_4(self):
        url = reverse("sign_up_view")
        data = {
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    '''이메일 중복 확인을 위한 유저 생성'''
    def setUp(self):            
        self.user = User.objects.create_user(email='testgo@test.test',
                                             password='G1843514dadg23@')

    '''이메일 중복'''
    def test_signup_5(self):
        url = reverse("sign_up_view")
        data = {
            "email" : "testgo@test.test",
            "password": "123456"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    '''회원가입 성공!'''
    def test_signup_6(self):
        url = reverse("sign_up_view")
        data = {
            "email" : "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 201)

    '''이메일 전송 확인'''
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend") # 이메일 실제 전송x, 백엔드 이메일
    def test_signup_email_send_7(self):
        url = reverse("sign_up_view")
        data = {
            "email" : "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 201)

        # 이메일 비동기 전송으로 시간 연장 추가
        async def wait_for_email():
            while len(mail.outbox) < 1:
                await asyncio.sleep(0.1)

        asyncio.run(wait_for_email())

        self.assertEqual(len(mail.outbox), 1)


# 이메일 인증 TEST
class VerifyEmailViewTest(APITestCase):
    def setUp(self):            
        self.user = User.objects.create_user(email='test@test.test',
                                             password='abc123qw!')
    
    '''이메일 인증 전 유저 비활성화 확인'''
    def test_create_user_is_active_8(self):
        self.assertFalse(self.user.is_active)

    '''이메일 인증 성공'''
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend") # 이메일을 실제로 전송하지 않고 로컬 메모리에 저장하는 백엔드
    def test_verify_email_9(self):        
        user_id = urlsafe_b64encode(force_bytes(self.user.pk)).decode('utf-8')
        token = PasswordResetTokenGenerator().make_token(self.user)

        auth_url = f"https://nuriggun.xyz/user/verify-email/{user_id}/{token}/"

        response = self.client.get(auth_url)
        print(response)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://teamnuri.xyz/user/login.html")
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    '''이메일 인증 유효하지 않는 토큰'''
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend") # 이메일을 실제로 전송하지 않고 로컬 메모리에 저장하는 백엔드
    def test_verify_email_10(self):        
        user_id = urlsafe_b64encode(force_bytes(self.user.pk)).decode('utf-8')
        token = PasswordResetTokenGenerator().make_token(self.user)

        auth_url1 = f"https://nuriggun.xyz/user/verify-email/no{user_id}/{token}/"

        response = self.client.get(auth_url1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://teamnuri.xyz/user/password_reset_failed.html")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        auth_url2 = f"https://nuriggun.xyz/user/verify-email/{user_id}/no{token}/"

        response = self.client.get(auth_url2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://teamnuri.xyz/user/password_reset_failed.html")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


# 로그인 인증 TEST
class LoginViewTest(APITestCase):
    def setUp(self):            
        self.user = User.objects.create_user(email='test@test.test', password='abc123qw!', is_active = True)

    '''이메일 인증 X'''
    def test_login_11(self):
        self.user.is_active = False
        self.user.save()

        url = reverse("login_view")
        data = {
            "email" : "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 401)

    '''비밀번호 빈값'''
    def test_login_12(self):
        url = reverse("login_view")
        data = {
            "email" : "test@test.test",
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    '''비밀번호 다름'''
    def test_login_13(self):
        url = reverse("login_view")
        data = {
            "email" : "test@test.test",
            "password": "123ABDqw!"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 401)

    '''이메일 빈값'''
    def test_login_14(self):
        url = reverse("login_view")
        data = {
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    '''이메일 다름'''
    def test_login_15(self):
        url = reverse("login_view")
        data = {
            "email" : "test123@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 401)

    '''이메일/비밀번호 빈값'''
    def test_login_16(self):
        url = reverse("login_view")
        data = {

        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 400)
    
    '''로그인 성공!'''
    def test_login_17(self):
        url = reverse("login_view")
        data = {
            "email" : "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 200)


# 소셜 로그인
class KakaoLoginViewTest(APITestCase):
    pass