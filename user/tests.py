from rest_framework.test import APITestCase, override_settings
from django.urls import reverse
from user.models import User
from django.core import mail
import asyncio


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
        