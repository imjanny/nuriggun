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
    def setUp(self):
        '''회원가입 : 이메일 중복 확인을 위한 유저 생성'''
        self.user = User.objects.create_user(
            email='testgo@test.test', password='G1843514dadg23@')
        
    def test_signup_1(self):
        '''회원가입 : 비밀번호 유효성 검사'''
        url = reverse("sign_up_view")
        data = {
            "email": "test@test.test",
            "password": "123456"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_signup_2(self):
        '''회원가입 : 이메일/비밀번호 빈값'''
        url = reverse("sign_up_view")
        data = {
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_signup_3(self):
        '''회원가입 : 이메일 중복'''
        url = reverse("sign_up_view")
        data = {
            "email": "testgo@test.test",
            "password": "123456"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_signup_4(self):
        '''회원가입 : 성공! (+이메일 전송 확인)'''
        url = reverse("sign_up_view")
        data = {
            "email": "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

        # 이메일 비동기 전송으로 시간 연장 추가
        async def wait_for_email(max_seconds=5):
            elapsed_seconds = 0
            while len(mail.outbox) < 1 and elapsed_seconds < max_seconds:
                await asyncio.sleep(0.1)
                elapsed_seconds += 0.1
            if len(mail.outbox) < 1:
                raise TimeoutError("이메일을 기다리는 동안 시간 초과가 발생했습니다.")

        asyncio.run(wait_for_email(max_seconds=5))

        self.assertEqual(len(mail.outbox), 1)


# 이메일 인증 TEST
class VerifyEmailViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.test', password='abc123qw!')
        self.user_id = urlsafe_b64encode(
            force_bytes(self.user.pk)).decode('utf-8')
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    def test_create_user_is_active_10(self):
        '''이메일 인증 : 인증 전 유저 비활성화 확인'''
        self.assertFalse(self.user.is_active)

    def test_verify_email_11(self):
        '''이메일 인증 : 유효하지 않는 토큰 값'''
        invalid_token = self.token + 'invalid'
        auth_url = f"https://nuriggun.xyz/user/verify-email/{self.user_id}/{invalid_token}/"

        response = self.client.get(auth_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, "https://teamnuri.xyz/user/password_reset_failed.html")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_verify_email_12(self):
        '''이메일 인증 : 유효하지 않는 user_id'''
        invalid_user_id = urlsafe_b64encode(force_bytes(6)).decode('utf-8')
        auth_url = f"https://nuriggun.xyz/user/verify-email/{invalid_user_id}/{self.token}/"

        response = self.client.get(auth_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, "https://teamnuri.xyz/user/password_reset_failed.html")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_verify_email_13(self):
        '''이메일 인증 : 성공! 활성화 확인!'''
        auth_url = f"https://nuriggun.xyz/user/verify-email/{self.user_id}/{self.token}/"

        response = self.client.get(auth_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://teamnuri.xyz/user/login.html")

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


# 로그인 TEST
class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.test', password='abc123qw!', is_active=True)

    def test_login_20(self):
        '''로그인 : 이메일 인증 X'''
        self.user.is_active = False
        self.user.save()

        url = reverse("login_view")
        data = {
            "email": "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_login_21(self):
        '''로그인 : 이메일/비밀번호 빈값'''
        url = reverse("login_view")
        data = {
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_login_22(self):
        '''로그인 : 비밀번호 다름'''
        url = reverse("login_view")
        data = {
            "email": "test@test.test",
            "password": "123ABDqw!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_login_23(self):
        '''로그인 : 이메일 다름'''
        url = reverse("login_view")
        data = {
            "email": "test123@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_login_24(self):
        '''로그인 : 성공!'''
        url = reverse("login_view")
        data = {
            "email": "test@test.test",
            "password": "abc123qw!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)


# 비밀번호 재설정 TEST
class PasswordResetViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.test', password='abc123qw!')
        self.user_id = urlsafe_b64encode(
            force_bytes(self.user.pk)).decode('utf-8')
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    def test_password_reset_email_send_30(self):
        '''비밀번호 재설정 이메일 전송 : 잘못된 이메일'''
        url = reverse("rest_password_reset_view")
        data = {
            "email": "test12@test.test"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_email_send_31(self):
        '''비밀번호 재설정 이메일 전송 : 이메일 빈값'''
        url = reverse("rest_password_reset_view")
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_email_send_32(self):
        '''비밀번호 재설정 이메일 전송 : 성공!'''
        url = reverse("rest_password_reset_view")
        data = {
            "email": "test@test.test"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        async def wait_for_email(max_seconds=5):
            elapsed_seconds = 0
            while len(mail.outbox) < 1 and elapsed_seconds < max_seconds:
                await asyncio.sleep(0.1)
                elapsed_seconds += 0.1
            if len(mail.outbox) < 1:
                raise TimeoutError("이메일을 기다리는 동안 시간 초과가 발생했습니다.")

        asyncio.run(wait_for_email(max_seconds=5))

        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_token_check_33(self):
        '''비밀번호 재설정 토큰 확인 : 유효하지 않는 토큰 값'''
        invalid_token = self.token + 'invalid'
        url = reverse("password_reset_confirm",
                      args=(self.user_id, invalid_token))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"https://teamnuri.xyz/user/password_reset_failed.html")
        
    def test_password_reset_token_check_34(self):
        '''비밀번호 재설정 토큰 확인 : 유효하지 않는 user_id'''
        invalid_user_id = urlsafe_b64encode(force_bytes(6)).decode('utf-8')
        url = reverse("password_reset_confirm", args=(invalid_user_id, self.token))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_password_reset_token_check_35(self):
        '''비밀번호 재설정 토큰 확인 : 성공!'''
        url = reverse("password_reset_confirm",
                      args=(self.user_id, self.token))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f"https://teamnuri.xyz/user/password_reset_confirm.html?id={self.user_id}&token={self.token}")

    def test_password_reset_confirm_40(self):
        '''비밀번호 재설정 진행 : 비밀번호 다름'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$nad",
            "password2": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_41(self):
        '''비밀번호 재설정 진행 : 비밀번호 유효성 실패'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "1234",
            "password2": "1234",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_42(self):
        '''비밀번호 재설정 진행 : 비밀번호 빈값'''
        url = reverse("password_reset_confirm_view")
        data = {
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_43(self):
        '''비밀번호 재설정 진행 : 유효하지 않는 토큰 값'''
        invalid_token = self.token + 'invalid'
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "password2": "qEadg423$#hbnad",
            "token": invalid_token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 401)

    def test_password_reset_confirm_44(self):
        '''비밀번호 재설정 진행 : 유효하지 않는 uidb64 값'''
        invalid_user_id = urlsafe_b64encode(force_bytes(21)).decode('utf-8')
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "password2": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": invalid_user_id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_45(self):
        '''비밀번호 재설정 진행 : 성공!(후 링크 클릭)'''
        url = reverse("password_reset_confirm_view")
        data = {
            "password": "qEadg423$#hbnad",
            "password2": "qEadg423$#hbnad",
            "token": self.token,
            "uidb64": self.user_id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)

        # 링크 클릭
        url = reverse("password_reset_confirm",
                      args=(self.user_id, self.token))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, "https://teamnuri.xyz/user/password_reset_failed.html")


# 비밀번호 변경 TEST
class PasswordChangeViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.test', password='abc123qw!')
        self.client.force_authenticate(user=self.user)

        self.user_1 = User.objects.create_user(
            email='test2@test.test', password='abc123qw1!')

    def test_password_change_50(self):
        '''비밀번호 변경 : 로그인X'''
        self.client.force_authenticate(user=None)  # 인증 해제
        user_id = self.user.id
        url = reverse("password_change_view", kwargs={"user_id": user_id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, 401)

    def test_password_change_51(self):
        '''비밀번호 변경 : 다른 user_id의 비밀번호 변경 진행'''
        user_id = self.user_1.id
        url = reverse("password_change_view", kwargs={"user_id": user_id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, 403)

    def test_password_change_52(self):
        '''비밀번호 변경 : 없는 user_id의 비밀번호 변경 진행'''
        user_id = 999
        url = reverse("password_change_view", kwargs={"user_id": user_id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, 404)

    def test_password_change_53(self):
        '''비밀번호 변경 : data 빈값'''
        user_id = self.user.id
        url = reverse("password_change_view", kwargs={"user_id": user_id})
        data = {}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_change_54(self):
        '''비밀번호 변경 : 비밀번호/비밀번호 확인 다름'''
        user_id = self.user.id
        url = reverse("password_change_view", kwargs={"user_id": user_id})
        data = {
            "password": "1234",
            "password2": "1234asdf@dsg453"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_change_55(self):
        '''비밀번호 변경 : 비밀번호 유효성 검사'''
        user_id = self.user.id
        url = reverse("password_change_view", kwargs={"user_id": user_id})
        data = {
            "password": "1234",
            "password2": "1234"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_change_56(self):
        '''비밀번호 변경 : 비밀번호 변경 성공!'''
        user_id = self.user.id
        url = reverse("password_change_view", kwargs={"user_id": user_id})
        data = {
            "password": "1234asdf@dsg453",
            "password2": "1234asdf@dsg453"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
