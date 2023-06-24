from rest_framework import serializers
from article.models import Article, Comment


class HomeSerializer(serializers.ModelSerializer):
    '''메인페이지 용 게시글 시리얼라이저'''
    comments_count = serializers.SerializerMethodField()
    great_count = serializers.SerializerMethodField()
    sad_count = serializers.SerializerMethodField()
    angry_count = serializers.SerializerMethodField()
    good_count = serializers.SerializerMethodField()
    subsequent_count = serializers.SerializerMethodField()
    reaction_count = serializers.SerializerMethodField()

    def get_great_count(self, obj):
        return obj.great.count()
    
    def get_sad_count(self, obj):
        return obj.sad.count()
    
    def get_angry_count(self, obj):
        return obj.angry.count()
    
    def get_good_count(self, obj):
        return obj.good.count()
    
    def get_subsequent_count(self, obj):
        return obj.subsequent.count()
    
    def get_reaction_count(self, obj):
        return sum([
            obj.great.count(),
            obj.sad.count(),
            obj.angry.count(),
            obj.good.count(),
            obj.subsequent.count()
        ])
    
    def get_comments_count(self, obj):
        return obj.comment.count()
    
    class Meta:
        model = Article
        fields = "__all__"
#---------------------------- 게시글 ----------------------------

class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    reaction = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk, 'emial': obj.user.email}

    def get_reaction(self, obj):
        reaction_data = {
            'great': obj.great.count(),
            'sad': obj.sad.count(),
            'angry': obj.angry.count(),
            'good': obj.good.count(),
            'subsequent': obj.subsequent.count()
        }
        return reaction_data

    def get_comments_count(self, obj):
        return obj.comment.count()

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'user', 'created_at',
                  'updated_at', 'reaction', 'category', 'image', 'image_content', 'comments_count']


class ArticleCreateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Article
        fields = ("pk", "user", "title", "content",
                  "category", "image", "image_content", "created_at", "updated_at")


class ArticlesUpdateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}

    class Meta:
        model = Article
        fields = ("pk", "user", "title",
                  "content", "image", "image_content", "CATEGORIES")


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    reaction = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "id": obj.user.id, }

    def get_reaction(self, obj):
        reaction_data = {
            'great': obj.great.count(),
            'sad': obj.sad.count(),
            'angry': obj.angry.count(),
            'good': obj.good.count(),
            'subsequent': obj.subsequent.count()
        }
        return reaction_data

    class Meta:
        model = Article
        fields = ["id", "title", "user", "image",
                  "created_at", "category", "reaction"]


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
        fields = ["title","content","id",]