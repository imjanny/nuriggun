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
    def test_signup_1(self):
        '''비밀번호 유효성 검사'''
        url = reverse("sign_up_view")
        data = {
            "email": "test@test.test",
            "password": "123456"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_signup_2(self):
        '''비밀번호 빈값'''
        url = reverse("sign_up_view")
        data = {
            "email": "test@test.test"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_signup_3(self):
        '''이메일 빈값'''
        url = reverse("sign_up_view")
        data = {
            "password": "123456"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_signup_4(self):
        '''이메일/비밀번호 빈값'''
        url = reverse("sign_up_view")
        data = {
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def setUp(self):
        '''이메일 중복 확인을 위한 유저 생성'''
        self.user = User.objects.create_user(
            email='testgo@test.test', password='G1843514dadg23@')

    def test_signup_5(self):
        '''이메일 중복'''
        url = reverse("sign_up_view")
        data = {
            "email": "testgo@test.test",
            "password": "123456"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_signup_6(self):
        '''회원가입 성공!'''
        url = reverse("sign_up_view")
        data = {
            "email": "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 201)

    # 이메일 실제 전송x, 백엔드 이메일
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_signup_email_send_7(self):
        '''이메일 전송 확인'''
        url = reverse("sign_up_view")
        data = {
            "email": "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        # print(response.data)
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
        self.user = User.objects.create_user(
            email='test@test.test', password='abc123qw!')
        self.user_id = urlsafe_b64encode(
            force_bytes(self.user.pk)).decode('utf-8')
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    def test_create_user_is_active_8(self):
        '''이메일 인증 전 유저 비활성화 확인'''
        self.assertFalse(self.user.is_active)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_verify_email_9(self):
        '''이메일 인증 : 유효하지 않는 토큰 값 -> 비활성화'''
        invalid_token = self.token + 'invalid'

        auth_url = f"https://nuriggun.xyz/user/verify-email/{self.user_id}/{invalid_token}/"

        response = self.client.get(auth_url)
        # print(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, "https://teamnuri.xyz/user/password_reset_failed.html")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_verify_email_10(self):
        '''이메일 인증 : 유효하지 않는 user_id -> 비활성화'''
        invalid_user_id = urlsafe_b64encode(force_bytes(6)).decode('utf-8')

        auth_url = f"https://nuriggun.xyz/user/verify-email/{invalid_user_id}/{self.token}/"

        response = self.client.get(auth_url)
        # print(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, "https://teamnuri.xyz/user/password_reset_failed.html")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    # 이메일을 실제로 전송하지 않고 로컬 메모리에 저장하는 백엔드
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_verify_email_11(self):
        '''이메일 인증 : 성공! 활성화 확인!'''
        auth_url = f"https://nuriggun.xyz/user/verify-email/{self.user_id}/{self.token}/"

        response = self.client.get(auth_url)
        # print(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://teamnuri.xyz/user/login.html")

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


# 로그인 인증 TEST
class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.test', password='abc123qw!', is_active=True)

    def test_login_12(self):
        '''이메일 인증 X'''
        self.user.is_active = False
        self.user.save()

        url = reverse("login_view")
        data = {
            "email": "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 401)

    def test_login_13(self):
        '''비밀번호 빈값'''
        url = reverse("login_view")
        data = {
            "email": "test@test.test",
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_login_14(self):
        '''비밀번호 다름'''
        url = reverse("login_view")
        data = {
            "email": "test@test.test",
            "password": "123ABDqw!"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 401)

    def test_login_15(self):
        '''이메일 빈값'''
        url = reverse("login_view")
        data = {
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_login_16(self):
        '''이메일 다름'''
        url = reverse("login_view")
        data = {
            "email": "test123@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 401)

    def test_login_17(self):
        '''이메일/비밀번호 빈값'''
        url = reverse("login_view")
        data = {}
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_login_18(self):
        '''로그인 성공!'''
        url = reverse("login_view")
        data = {
            "email": "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 200)


# 소셜 로그인
class KakaoLoginViewTest(APITestCase):
    pass


# 비밀번호 재설정 TEST
class PasswordResetViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.test', password='abc123qw!')
        self.user_id = urlsafe_b64encode(
            force_bytes(self.user.pk)).decode('utf-8')
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_email_send_19(self):
        '''이메일 전송 : 잘못된 이메일'''
        url = reverse("rest_password_reset_view")
        data = {
            "email": "test12@test.test"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_email_send_20(self):
        '''이메일 전송 : 이메일 빈값'''
        url = reverse("rest_password_reset_view")
        data = {}
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_email_send_21(self):
        '''이메일 전송 : 이메일 전송 성공!'''
        url = reverse("rest_password_reset_view")
        data = {
            "email": "test@test.test"
        }
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        async def wait_for_email():
            while len(mail.outbox) < 1:
                await asyncio.sleep(0.1)

        asyncio.run(wait_for_email())

        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_token_check_22(self):
        '''재설정 토큰 확인 : 유효하지 않는 토큰 값'''
        invalid_token = self.token + 'invalid'
        url = reverse("password_reset_confirm",
                      args=(self.user_id, invalid_token))
        response = self.client.get(url)
        # print(response)
        self.assertEqual(
            response.url, f"https://teamnuri.xyz/user/password_reset_failed.html")
        self.assertEqual(response.status_code, 302)

    def test_password_reset_token_check_23(self):
        '''재설정 토큰 확인 : 유효하지 않는 user_id ★★★★★ 재확인'''
        # invalid_user_id = urlsafe_b64encode(force_bytes(6)).decode('utf-8')
        # url = reverse("password_reset_confirm", args=(invalid_user_id, self.token))
        # response = self.client.get(url)
        # print(response)
        # self.assertEqual(response.url, f"https://teamnuri.xyz/user/password_reset_failed.html")
        # self.assertEqual(response.status_code, 404)

    def test_password_reset_token_check_24(self):
        '''재설정 토큰 확인 : 성공!'''
        url = reverse("password_reset_confirm",
                      args=(self.user_id, self.token))
        response = self.client.get(url)
        # print(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"https://teamnuri.xyz/user/password_reset_confirm.html?id={self.user_id}&token={self.token}")

    def test_password_reset_confirm_25(self):
        '''재설정 진행 : 비밀번호 다름'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$nad",
            "password2": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_26(self):
        '''재설정 진행 : 비밀번호 유효성 실패'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "1234",
            "password2": "1234",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_27(self):
        '''재설정 진행 : 비밀번호 빈값'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_28(self):
        '''재설정 진행 : 유효하지 않는 토큰 값'''
        invalid_token = self.token + 'invalid'
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "password2": "qEadg423$#hbnad",
            "token": invalid_token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 401)

    def test_password_reset_confirm_29(self):
        '''재설정 진행 : 유효하지 않는 uidb64 값'''
        invalid_user_id = urlsafe_b64encode(force_bytes(21)).decode('utf-8')
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "password2": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": invalid_user_id
        }
        response = self.client.put(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_30(self):
        '''재설정 진행 : 성공!'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "password2": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm_30(self):
        '''재설정 후 링크 클릭'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "password2": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        url = reverse("password_reset_confirm",
                      args=(self.user_id, self.token))
        response = self.client.get(url)
        # print(response.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, "https://teamnuri.xyz/user/password_reset_failed.html")

        # redirected_url = response.url
        # response = self.client.get(redirected_url)
        # print(response)

        # # self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.url, "https://teamnuri.xyz/index.html")
