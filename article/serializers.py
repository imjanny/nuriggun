from rest_framework import serializers
from article.models import Article, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.email

    class Meta:
        model = Comment
        exclude = ("article",) 


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)
        

class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_set = CommentSerializer(many= True) # 게시글에 대한 댓글 불러오기 (comment_set = related_name)

    def get_user(self, obj):
        return obj.user.email # user값을 email로 가져오겠다.
    
    class Meta:
        model = Article
        fields = '__all__'


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("title", "image", "content")

    
class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.email
   
    
    def get_comment_count(self, obj):
        return obj.comment_set.count()

class Meta:
        model = Article
        fields = ("pk", "title", "image", "user") # 선택한 항목만 가져오겠다.
