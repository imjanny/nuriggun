from rest_framework import serializers
from article.models import Article, Comment



class HomeSerializer(serializers.ModelSerializer):
    '''메인페이지 용 게시글 시리얼라이저'''
    count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    def get_count(self, obj):
        return Article.objects.count()
    
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


    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}


    def get_reaction(self, obj):
        reaction_data = {
            'great': obj.great.count(),
            'sad': obj.sad.count(),
            'angry': obj.angry.count(),
            'good': obj.good.count(),
            'subsequent': obj.subsequent.count()
        }
        return reaction_data
    

    # def get_reaction(self, obj):
    #     reaction_data = {
    #         'great': 0,
    #         'sad': 0,
    #         'angry': 0,
    #         'good': 0,
    #         'subsequent': 0
    #     }
    #     reactions = obj.articlereaction_set.all()
    #     for reaction in reactions:
    #         if reaction.great:
    #             reaction_data['great'] += 1
    #         elif reaction.sad:
    #             reaction_data['sad'] += 1
    #         elif reaction.angry:
    #             reaction_data['angry'] += 1
    #         elif reaction.good:
    #             reaction_data['good'] += 1
    #         elif reaction.subsequent:
    #             reaction_data['subsequent'] += 1
    #     return reaction_data

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'user', 'created_at', 'updated_at', 'reaction', 'category', 'image']




class ArticleCreateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Article
        fields = ("pk", "user", "title", "content",
                  "category", "image","created_at", "updated_at")

   


class ArticlesUpdateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {'nickname': obj.user.nickname, 'pk': obj.user.pk}

    class Meta:
        model = Article
        fields = ("pk", "user", "title",
                  "content", "image", "CATEGORIES")
   



class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "id": obj.user.id,}

    class Meta:
        model = Article
        fields = ["id", "title", "user", "image", "created_at"]
         


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