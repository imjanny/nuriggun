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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성시간")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정시간")
   
#--------------------- 좋아요 관련 나중에 작성할 예정 -------------------------










#------------------------- 테스트 코드 함수 -------------------------
    def get_absolute_url(self):
        return reverse("articles:article_detail_view", kwargs={"article_id": self.pk})

    def __str__(self):
        return str(self.title)
    
# 댓글 models
class Comment(models.Model):
    class Meta:
        db_table = "comment"
        ordering = ["-comment_created_at"]  # 댓글 최신순 정렬

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comment")
    comment = models.TextField("댓글")
    comment_created_at = models.DateTimeField(auto_now_add=True)
    comment_updated_at = models.DateTimeField(auto_now_add=True)

#--------------------- 댓글 좋아요 관련 나중에 작성할 예정 -------------------------


    def __str__(self):
        return str(self.comment)
