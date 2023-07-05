from django.urls import reverse
from rest_framework.test import APITestCase
from django.test import TestCase,RequestFactory
from rest_framework import status
from .models import Article
from .views import HomeView
from user.models import User
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
# from faker import Faker
from .serializers import ArticleSerializer


'''임시 이미지 파일'''

def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


'''게시글 TEST'''

class AriticleAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls): 
            cls.user_data = {
                            "email" : "1@1.111",
                            "password" : "1234"
                             } 
            cls.article_data = {
                                "title" : "test title",
                                "content" : "test content",
                                "category" : "문화" } 
            cls.user = User.objects.create_user("1@1.111","1234") 
           

  
    def setUp(self):
        self.access_token = self.client.post(
            reverse("login_view"), self.user_data).data["access"]
    
    
    
    '''로그인 안되었을때'''
    def test_fail_if_not_logged_in(self): 
        url = reverse("article_view")
        response = self.client.post(url, self.article_data)
        self.assertEqual(response.status_code, 401)
        # print(response.data)

    

    '''게시글 보기(아무것도 없을 경우)'''
    def test_get_article_list_empty(self):
        response = self.client.get(path=reverse("article_list", kwargs={"user_id": self.user.id}))
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        


    
    ''' 게시물 조회'''
    def test_article_list(self):
        self.article = []
        for _ in range(3):
            self.article.append(
                Article.objects.create(**self.article_data, user=self.user)
            )
        response = self.client.get(
            path=reverse("article_list", kwargs={"user_id": self.user.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    
    
    '''게시글 작성시 타이틀이 없을 경우'''
    def test_create_article_without_title(self):
        article_data_without_title = {
            "content": "test content",
            "category": "test category",
        }

        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)

        # image_file을 article_data에 추가
        article_data_without_title["image"] = image_file

        response = self.client.post(
            path=reverse("article_view"),
            data=encode_multipart(data=article_data_without_title, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        print(response.data)


    '''게시글 작성시 카테고리가 없을 경우 '''
    def test_create_article_without_category(self):
        article_data_without_category = {
            "title": "test title",
            "content": "test content",
        }

        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)

        # image_file을 article_data에 추가
        article_data_without_category["image"] = image_file

        response = self.client.post(
            path=reverse("article_view"),
            data=encode_multipart(data=article_data_without_category, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)
        print(response.data)


    '''전부다 작성하지 않는 경우'''
    def test_create_article_without_fields(self):
        article_data_without_fields = {}

        response = self.client.post(
            path=reverse("article_view"),
            data=article_data_without_fields,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("content", response.data)
        self.assertIn("category", response.data)
        self.assertIn("image", response.data)
        print(response.data)

    
    '''게시글 작성시 이미지가 없을 경우 '''
    def test_create_article_without_image(self):
        article_data_without_image = {
            "title": "test title",
            "content": "test content",
            "category": "test category",
        }

        response = self.client.post(
            path=reverse("article_view"),
            data=article_data_without_image,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", response.data)
        print(response.data)


        
    ''' article 생성 '''
    def test_create_article(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)

        temp_file2 = tempfile.NamedTemporaryFile()
        temp_file2.name = "image2.png"
        image_file2 = get_temporary_image(temp_file2)
        image_file2.seek(0)

        self.article_data["image"] = image_file

        response = self.client.post(
            path=reverse("article_view"),
            data=encode_multipart(data=self.article_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # print(response.data)

    def test_home_view():
    # RequestFactory를 사용하여 GET 요청 생성
        factory = RequestFactory()
        request = factory.get("/home/?order=main")
        
        # HomeView 인스턴스 생성
        view = HomeView()
        
        # get 메서드 호출
        response = view.get(request)
        
        # 응답 코드 확인
        assert response.status_code == 200
        
        # 응답 데이터 검증
        data = response.data
        
        # TODO: 응답 데이터에 대한 검증 로직 작성
        
        # 페이징 정보 확인
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data
    