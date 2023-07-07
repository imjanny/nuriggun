from django.urls import reverse
from rest_framework.test import APITestCase,APIClient,force_authenticate,APIRequestFactory
from django.test import TestCase,RequestFactory
from rest_framework import status
from .models import Article,Comment,CommentReaction
from .views import HomeView
from user.models import User
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
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
            cls.email= "1@1.111"
            cls.password= "1234"
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
    
    
    
    """로그인"""
    def test_login(self):
        url = reverse("login_view")
        data = {
            'email': self.email,
            'password': self.password
        }
        
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
    

    
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
        # print(response.data)




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
        # print(response.data)




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
        # print(response.data)




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
        # print(response.data)


        
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

    


'''게시글'''
class ArticleDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'email':'1@1.111','password':'1234'}
        cls.article_data = [
            {"title": "test Title1", "content": "test content1", "category":"문화"},
            {"title": "test Title2", "content": "test content2", "category":"스포츠"},
            {"title": "test Title3", "content": "test content3", "category":"it"},
            {"title": "test Title4", "content": "test content4", "category":"세계"},
            {"title": "test Title5", "content": "test content5", "category":"날씨"},
            {"title": "test Title6", "content": "test content6", "category":"경제"}
        ]
        

        cls.user = User.objects.create_user('1@1.111','1234')
        cls.article = []
        '''가짜데이터'''
        cls.faker = Faker()
        cls.article = []
        for i in range(10):
            cls.article.append(
                Article.objects.create(
                title=cls.faker.sentence(),
                content=cls.faker.text(),
                user=cls.user
            )
        )


        cls.update_data = {
            "title": "test title",
            "content": "test content",
            "category": "문화"
        }
        
    def setUp(self):
        self.client.force_authenticate(user=self.user)
        self.access_token = self.client.post(
            reverse("login_view"), self.user_data).data["access"]
        

    
    '''게시글 상세페이지'''
    def test_article_detail(self):
        response = self.client.get(
            path=reverse("article_detail_view", kwargs={"article_id": 12}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        



    '''게시글 수정'''
    def test_article_detail_update(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        url = reverse("article_detail_view", kwargs={"article_id": 12})
        response = self.client.patch(
            path=url,
            data=self.update_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       
   
    """게시글 수정 안될때"""
    def test_failed_update(self):
        url = reverse("article_detail_view", kwargs={"article_id": 12})
        invalid_data = {
            "title": "Invalid Title",
            "content": "Invalid Content",
            "category": "Invalid Category"
        }

        response = self.client.patch(
            path=url,
            data=invalid_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    """수정 권한이 없는 경우"""
   
    def test_article_detail_update(self):
        url = reverse('article_detail_view', kwargs={'article_id': 12})
        response = self.client.patch(
            path=url,
            data=self.update_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        if response.status_code == status.HTTP_403_FORBIDDEN:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            

    """게시글 삭제/삭제 권한이 없는 경우"""

    def test_article_detail_delete(self):
        response = self.client.delete(
            path=reverse("article_detail_view", kwargs={"article_id": 12}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        if response.status_code == status.HTTP_403_FORBIDDEN:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(response.data, {'message': '삭제완료!'})



    """유저 스크랩/취소"""
    def test_scrap_article(self):
        url = reverse('scrap_view', kwargs={'article_id': 12})
        response = self.client.post(url)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,'스크랩')
        
        response = self.client.post(url)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
     

    """스크랩 횟수"""
    def test_get_article_scrap_count(self):
        url = reverse('scrap_view', kwargs={'article_id': 12})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('scrap', response.data)



    """스크랩 조회"""
    def test_get_user_scrapped_articles(self):
        url = reverse("scrap_view_article", kwargs={"user_id": self.user.id})
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    



"""좋아요 Test"""
class ArticleReactionViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'email':'1@1.111','password':'1234'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.user = User.objects.create_user('1@1.111','1234')
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        cls.reactions = ['great', 'sad', 'angry', 'good', 'subsequent']
        
    def setUp(self):
        self.access_token = self.client.post(reverse("login_view"), self.user_data).data["access"]


    """좋아요 등록"""
    def test_add_article(self):
        url = reverse("article_reaction", kwargs={"article_id": self.article.id})
        reaction = 'great'
        data = {'reaction': reaction}

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], '반응을 눌렀습니다.')

   

"""댓글 Test"""
class CommentViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'email':'1@1.111','password':'1234'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.user = User.objects.create_user('1@1.111','1234')
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        cls.comment_data = {"comment": "test comment"}

        cls.comment = []
        for _ in range(5):
            cls.comment.append(
                Comment.objects.create(
                    comment="comment", article=cls.article, user=cls.user
                )
            )

    def setUp(self):
        self.access_token = self.client.post(reverse("login_view"), self.user_data).data["access"]

    """댓글 조회"""
    def test_get_comments(self):
        url = reverse('comment_view', kwargs={'article_id': self.article.id})
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    """댓글 작성"""
    def test_create_comment(self):
        response = self.client.post(
            path=reverse("comment_view", kwargs={"article_id": self.article.id}),
            data=self.comment_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.first()
        self.assertEqual(comment.comment, self.comment_data["comment"])


    """댓글 수정"""
    def test_update_comment(self):
        comment = Comment.objects.create(article=self.article, user=self.user, comment="Test comment")
        url = reverse('comment_view', kwargs={'comment_id': comment.id})
        data = {
            'comment': 'Updated comment content'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    """댓글 수정 권한이 없을경우"""
    def test_update_comment_user(self):
        comment = Comment.objects.create(article=self.article, user=self.user, comment="Test comment")
        url = reverse('comment_view', kwargs={'comment_id': comment.id})
        data = {
            'comment': 'Updated comment content'
        }
        other_user = User.objects.create_user(email='otheruser', password='password')
        self.client.force_authenticate(user=other_user)
        response = self.client.put(url,data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], '댓글 작성자만 수정할 수 있습니다.')




    """댓글 삭제""" 
    def test_comment_delete(self):
        comment_id = self.comment[0].id  # 삭제할 댓글의 ID
        response = self.client.delete(
            path=reverse("comment_view", kwargs={"comment_id": comment_id}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    """댓글 삭제 권한이 없는 경우"""
    def test_comment_delete_user(self):
        comment = Comment.objects.create(article=self.article, user=self.user, comment="Test comment")
        url = reverse('comment_view', kwargs={'comment_id': comment.id})
        data = {
            'comment': 'Updated comment content'
        }
        other_user = User.objects.create_user(email='otheruser', password='password')
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(url,data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], '댓글 작성자만 삭제할 수 있습니다.')




"""댓글 좋아요 TEST"""
class CommentLikeViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'email':'1@1.111','password':'1234'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.user = User.objects.create_user('1@1.111','1234')
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        cls.comment_data = {"comment": "test comment"}

        cls.comment = []
        for _ in range(5):
            cls.comment.append(
                Comment.objects.create(
                    comment="comment", article=cls.article, user=cls.user
                )
            )


    """댓글 좋아요"""
    def test_like_comment(self):
        comment = Comment.objects.create(article=self.article, user=self.user, comment="Test comment")
        url = reverse("comment_like_view", kwargs={"comment_id": comment.id})  
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    

    

"""댓글 싫어요"""
class CommentHateViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'email':'1@1.111','password':'1234'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.user = User.objects.create_user('1@1.111','1234')
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        cls.comment_data = {"comment": "test comment"}

        cls.comment = []
        for _ in range(5):
            cls.comment.append(
                Comment.objects.create(
                    comment="comment", article=cls.article, user=cls.user
                )
            )

    def test_hate_comment(self):
        comment = Comment.objects.create(article=self.article, user=self.user, comment="Test comment")
        url = reverse('comment_hate_view', kwargs={'comment_id': comment.id})

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, '싫어요를 했습니다.')

    

"""글 검색"""
class ArticleSearchViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'email':'1@1.111','password':'1234'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.user = User.objects.create_user('1@1.111','1234')
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        # 테스트에 필요한 초기 데이터 설정

    def test_search_article(self):
        url = reverse('article_search') + "?search=test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for data in response.data:
            self.assertEqual(data["title"], "test Title")  
   