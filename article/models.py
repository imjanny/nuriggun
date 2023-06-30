from django.db import models
from user.models import User
import os
from datetime import date
from django.urls import reverse  # 테스트 코드


#------------------------- 게시글 모델 -------------------------

class Article(models.Model):
    class Meta:
        db_table = "Article"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    title = models.CharField(max_length=50, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    image = models.ImageField(verbose_name="게시글 이미지")
    image_content = models.TextField(verbose_name="사진 설명", null=True, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성시간")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정시간")
    great = models.ManyToManyField(User, blank=True, related_name="great")
    sad = models.ManyToManyField(User, blank=True, related_name="sad")
    angry = models.ManyToManyField(User, blank=True, related_name="angry")
    good = models.ManyToManyField(User, blank=True, related_name="good")
    subsequent = models.ManyToManyField(User, blank=True, related_name="subsequent")
    summary = models.TextField(max_length=300, blank=True, verbose_name="요약")

    
#------------------------- 카테고리 모델 -------------------------
    
    CATEGORIES = (

        ('it', 'it'),
        ('경제', 'economy'),
        ('문화', 'culture'),
        ('스포츠', 'sport'),
        ('날씨', 'weather'),
        ('세계', 'world'),

    )
    category = models.CharField("카테고리", choices=CATEGORIES, max_length=10, blank=False, null=False)

#------------------------- 스크랩(북마크) -------------------------
    
    #스크랩(북마크) : 게시글과 사용자를 연결하는 Many To Many 필드
    scrap = models.ManyToManyField(User, blank=True, related_name='scrap')
    
    # 북마크 갯수 세는 함수
    def count_scrap(self):
        return self.scrap.count()
    
#------------------------- 테스트 코드 함수 -------------------------
    
    def get_absolute_url(self):
        return reverse("article_detail_view", kwargs={"article_id": self.pk})

    def __str__(self):
        return str(self.title)
    

#--------------------- 게시글 반응 ------------------


class ArticleReaction(models.Model):
    class Meta:
        db_table = "Articlereaction"

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="해당 게시글")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    great = models.BooleanField(default=False)
    sad = models.BooleanField(default=False)
    angry = models.BooleanField(default=False)
    good = models.BooleanField(default=False)
    subsequent = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.article)

#------------------------- 댓글 모델 -------------------------

class Comment(models.Model):
    class Meta:
        db_table = "comment"
        ordering = ["-comment_created_at"]  # 댓글 최신순 정렬

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comment")
    comment = models.TextField("댓글")
    comment_created_at = models.DateTimeField(auto_now_add=True)
    comment_updated_at = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default=0)
    hate_count = models.PositiveIntegerField(default=0)

class CommentReaction(models.Model):
    class Meta:
        db_table = "commentreaction"
        
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, blank=True, related_name="like")
    hate = models.ManyToManyField(User, blank=True, related_name="hate")
