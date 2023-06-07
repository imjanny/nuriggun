from rest_framework import serializers
from article.models import Article, Comment


#---------------------------- 게시글 ----------------------------

class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    article_created_at = serializers.DateTimeField(
        format='%Y-%m-%d', read_only=True)
    article_updated_at = serializers.DateTimeField(
        format='%Y-%m-%d', read_only=True)

    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}


    # def get_name(self, obj):
    #     return dir.user.nickname
    
    # def get_user(self, obj):
    #     return dir.user.id


    class Meta:
        model = Article
        fields = '__all__'



class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("pk", "user", "title", "content",
                  "image", "category", "created_at", "updated_at")

   


class ArticlesUpdateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}

    class Meta:
        model = Article
        fields = ("pk", "user", "title",
                  "content", "image", "category")
   



class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    changed_image = serializers.ImageField()

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "id": obj.user.id,}

    class Meta:
        model = Article
        fields = ["id", "title", "user", "image",]
         


#---------------------------- 댓글 ----------------------------


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_created_at = serializers.DateTimeField(
        format='%Y-%m-%d', read_only=True)
    comment_updated_at = serializers.DateTimeField(
        format='%Y-%m-%d', read_only=True)

    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}

    class Meta:
        model = Comment
        exclude = ('article',)  # 게시글 필드 빼고 보여주기 


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("comment",)



#---------------------------- 검색 기능 ----------------------------

class ArticleSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title","context","id",]