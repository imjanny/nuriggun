from rest_framework.test import APITestCase
from django.urls import reverse
from user.models import Message, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from django.contrib.auth import get_user_model

from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile


def get_temporary_image(temp_file):
    """ 임시 이미지 파일 """
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


# 쪽지 테스트 코드
class MessageTestView(APITestCase):
    """ 쪽지 테스트 코드 """
    @classmethod
    def setUpTestData(cls):
        cls.email = "test@test.com"
        cls.password = "test"
        cls.user_data = {'email': cls.email,
                         'password': cls.password,
                         'is_active': 'True'}
        cls.message_data = {
            'sender': 'test@test.com',
            'receiver': 'a@a.com',
            'title': 'test title',
            'content': 'test content'
        }
        cls.no_title = {
            'sender': cls.email,
            'receiver': 'a@a.com',
            'content': 'test content'

        }
        cls.no_receiver = {
            'sender': cls.email,
            'title': 'test title',
            'content': 'test content'
        }
        cls.no_content = {
            'sender': cls.email,
            'receiver': 'a@a.com',
            'title': 'test title'
        }
        cls.over_title = {
            'sender': cls.email,
            'receiver': 'a@a.com',
            'title': '고요한 숲 속, 울창한 나뭇잎 사이로 햇빛이 스며들어 아래 이끼 낀 땅에 얼룩덜룩한 무늬를 드리우고 있습니다. 새들은 선율적인 노래로 서로에게 세레나데를 부르며 자연의 교향곡을 만들었습니다. 부드러운 바람이 나무 사이로 속삭이며 나뭇잎을 바스락 거리고 상쾌한 소나무 향기를 가져옵니다.',
            'content': 'test content'
        }
        cls.nothing = {
            'sender': '',
            'receiver': '',
            'title': '',
            'content': ''
        }
        # cls.message = []
        # for _ in range(5):
        #     cls.message.append(
        #         Message.objects.create(
        #             sender='test@test.com', receiver='a@a.com', title='title 123', content='content 123')
        #     )
        cls.receiver = User.objects.create_user(
            'a@a.com', 'test', is_active='True')
        cls.user = User.objects.create_user(
            cls.email, cls.password, is_active='True')

    def setUp(self):
        self.access_token = self.client.post(
            reverse("login_view"), self.user_data).data["access"]

    def test_create_message_without_receiver(self):
        """ 받는 이 없는 쪽지 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.message_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_create_view"),
            data=encode_multipart(data=self.no_receiver, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_without_title(self):
        """ 제목 없는 쪽지 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.message_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_create_view"),
            data=encode_multipart(data=self.no_title, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_over_title(self):
        """ 100글자 넘어가는 제목으로 쪽지 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.message_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_create_view"),
            data=encode_multipart(data=self.over_title, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_over_content(self):
        """ 내용 없는 쪽지 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.message_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_create_view"),
            data=encode_multipart(data=self.no_content, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_without_image(self):
        """ 이미지 없는 쪽지 """
        response = self.client.post(
            path=reverse("message_create_view"),
            data=self.message_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.data["message"], "쪽지를 보냈습니다.")
        self.assertEqual(response.status_code, 200)

    def test_create_message_without_everything(self):
        """ 모든 조건(받는 사람, 제목, 내용, 이미지) 없는 쪽지 """
        response = self.client.post(
            path=reverse("message_create_view"),
            data=self.nothing,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_with_image(self):
        """ 모든 조건(받는 사람, 제목, 내용, 이미지) 만족하는 쪽지 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.message_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_create_view"),
            data=encode_multipart(data=self.message_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.data["message"], "쪽지를 보냈습니다.")
        self.assertEqual(response.status_code, 200)

    def test_inbox_list(self):
        """ 받은 쪽지함 """
        response = self.client.get(
            path=reverse("message_inbox_view"),
            data={"receiver": self.user.email},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sent_list(self):
        """ 보낸 쪽지함 """
        response = self.client.get(
            path=reverse("message_sent_view"),
            data={"sender": self.user.email},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_message_detail(self):
    #     """ 쪽지 상세페이지 """
    #     response = self.client.get(
    #         path=reverse("message_detail_view", kwargs={"message_id": self.message.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
    #     )
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_message_delete(self):
    #     """ 쪽지 삭제 """
    #     message_id = self.message[0].id
    #     response = self.client.delete(
    #         path=reverse("message_detail_view", kwargs={
    #                      "message_id": self.message.id}),
    #         HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
    #     )
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReplyTestView(APITestCase):
    """ 답장 테스트코드 """
    @classmethod
    def setUpTestData(cls):
        cls.email = "b@b.com"
        cls.receiver = "c@c.com"
        cls.password = "test"
        cls.user_data = {'email': cls.email,
                         'password': cls.password,
                         'is_active': 'True'}
        cls.reply_data = {
            'sender': cls.email,
            'receiver': cls.receiver,
            'title': 'test title',
            'content': 'test content'
        }
        cls.reply = Message.objects.create(**cls.reply_data)
        cls.no_title = {
            'sender': cls.email,
            'receiver': cls.receiver,
            'content': 'test content'
        }
        cls.no_content = {
            'sender': cls.email,
            'receiver': cls.receiver,
            'title': 'test title'
        }
        cls.over_title = {
            'sender': cls.email,
            'receiver': cls.receiver,
            'title': '고요한 숲 속, 울창한 나뭇잎 사이로 햇빛이 스며들어 아래 이끼 낀 땅에 얼룩덜룩한 무늬를 드리우고 있습니다. 새들은 선율적인 노래로 서로에게 세레나데를 부르며 자연의 교향곡을 만들었습니다. 부드러운 바람이 나무 사이로 속삭이며 나뭇잎을 바스락 거리고 상쾌한 소나무 향기를 가져옵니다.',
            'content': 'test content'
        }
        cls.nothing = {
            'sender': '',
            'receiver': '',
            'title': '',
            'content': ''
        }

        cls.sender = User.objects.create_user(
            'b@b.com', 'test', is_active='True')
        cls.receiver = User.objects.create_user(
            cls.receiver, cls.password, is_active='True')

    def setUp(self):
        self.access_token = self.client.post(
            reverse("login_view"), self.user_data).data["access"]

    def test_create_reply_without_title(self):
        """ 제목 없는 답장 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.reply_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_reply_view", kwargs={
                         'message_id': self.reply.id}),
            data=encode_multipart(data=self.no_title, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_reply_over_title(self):
        """ 100글자 넘어가는 제목으로 답장 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.reply_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_reply_view", kwargs={
                         'message_id': self.reply.id}),
            data=encode_multipart(data=self.over_title, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_over_content(self):
        """ 내용 없는 답장 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.reply_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_reply_view", kwargs={
                         'message_id': self.reply.id}),
            data=encode_multipart(data=self.no_content, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_without_image(self):
        """ 이미지 없는 답장 """
        response = self.client.post(
            path=reverse("message_reply_view", kwargs={
                         'message_id': self.reply.id}),
            data=self.reply_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.data["message"], "쪽지를 보냈습니다.")
        self.assertEqual(response.status_code, 200)

    def test_create_message_without_everything(self):
        """ 모든 조건(제목, 내용, 이미지) 없는 답장 """
        response = self.client.post(
            path=reverse("message_reply_view", kwargs={
                         'message_id': self.reply.id}),
            data=self.nothing,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_with_image(self):
        """ 모든 조건(제목, 내용, 이미지) 만족하는 답장 """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.reply_data["image"] = image_file

        response = self.client.post(
            path=reverse("message_reply_view", kwargs={
                         'message_id': self.reply.id}),
            data=encode_multipart(data=self.reply_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.data["message"], "쪽지를 보냈습니다.")
        self.assertEqual(response.status_code, 200)
