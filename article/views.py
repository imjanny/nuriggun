from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from article.models import Article, Comment, CommentReaction
from article.serializers import (
    HomeSerializer,
    ArticleSerializer,
    ArticleListSerializer,
    ArticleCreateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    ArticleSearchSerializer
    )
import datetime
from rest_framework import permissions
from .models import ArticleReaction

from user.models import User
from rest_framework import generics, filters



# ======== 메인페이지 관련 import =========
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Count
# ========= 메인페이지 view =========
class HomePagination(LimitOffsetPagination):
    default_limit = 10

    def get_limit(self, request):
        ordering = request.query_params.get("order", None)
        if ordering == "main":
            return 4  
        else:
            return self.default_limit  
    

class HomeView(APIView):
    '''홈-게시글'''
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = HomePagination

    def get(self, request):
        ordering = request.query_params.get("order", None)
        if ordering == "sub":
            articles = Article.objects.order_by("-created_at")
            print("서브")
        elif ordering == "main":
            articles = Article.objects.annotate(
                comments_count=Count("comment")
            ).order_by("-comments_count")
            print("메인")
        elif ordering is None:
            articles = Article.objects.all()

        paginator = self.pagination_class()
        paginated_articles = paginator.paginate_queryset(articles, request)

        serializer = HomeSerializer(paginated_articles, many=True)
        response_data = {
            'results': serializer.data,
            'order': ordering  
        }
        return paginator.get_paginated_response(response_data)
     
#------------------------------------- 게시글 생성 ------------------------------------- 

class ArticleView(APIView): 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
# ------------------------------------ 게시글 목록 -------------------------------------
    
    def get(self, request, category=None):
        if category:
            articles = Article.objects.filter(category=category)
        else:
            articles = Article.objects.all()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------------------------ 게시글 작성 -------------------------------------

    def post(self, request): 
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------ 게시글 리스트 보기 -------------------------------------      


class ArticleListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  
    
    def get(self, request, user_id):  
        articles = Article.objects.filter(user_id=user_id)
        serializer = ArticleListSerializer(articles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

# ------------------------------------ 게시글 상세페이지 -------------------------------------      

class ArticleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, article_id): # patch 원하는 것만 수정이 가능하다.!
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleCreateSerializer(
                article, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            article.delete()
            return Response({"message": "삭제완료!"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)


# ------------------------------------ 게시글 스크랩 -------------------------------------


class ScrapView(APIView):
    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user in article.scrap.all():
            article.scrap.remove(request.user)
            return Response('스크랩취소', status=status.HTTP_202_ACCEPTED)
        else:
            article.scrap.add(request.user)
            return Response('스크랩', status=status.HTTP_200_OK)


    def get(self, request, article_id):
        article = Article.objects.get(id=article_id)
        scrap_count = article.count_scrap()
        return Response({'scrap': scrap_count})
    
  

#------------------------------------ 게시글 스크랩 리스트 -------------------------------------

class ScrapListView(APIView):
    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user in article.scrap.all():
            article.scrap.remove(request.user)
            return Response('스크랩 취소', status=status.HTTP_200_OK)
        else:
            article.scrap.add(request.user)
            return Response('스크랩', status=status.HTTP_200_OK)    
   
   
# ----------------------------------- 스크랩 한 게시글 보기 -----------------------------------

    def get(self, request):
        user = request.user
        article = user.scrap.all()
        serializer = ArticleSerializer(article, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



#---------------------------------- 게시글 좋아요 5종 반응 ---------------------------------


class ArticleReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, article_id):
        try:
            article = get_object_or_404(Article, id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "게시글이 없습니다."}, status=404)

        reaction = request.data.get('reaction')

        if reaction in ['great', 'sad', 'angry', 'good', 'subsequent']:
            reaction_field = getattr(article, reaction) #getattr 아직 잘모르지만 나중에?

            if request.user in reaction_field.all():
                # 사용자가 이미 반응을 한 상태이므로 반응을 취소
                reaction_field.remove(request.user)
                return Response({"message": "반응을 취소했습니다."}, status=status.HTTP_200_OK)
            else:
                # 사용자가 반응을 하지 않은 상태이므로 반응을 추가
                reaction_field.add(request.user)
                return Response({"message": "반응을 눌렀습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "유효하지 않은 반응 타입입니다."}, status=status.HTTP_400_BAD_REQUEST)


#----------------------------------- 검색 기능 -----------------------------------


class ArticleSearchView(generics.ListCreateAPIView):
    search_fields = ["title", "content","id",]
    filter_backends = (filters.SearchFilter,)
    queryset = Article.objects.all()
    serializer_class = ArticleSearchSerializer

    
    

# ----- 댓글 시작 -----

class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 게시글 댓글 보기
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        comments = article.comment.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 댓글 작성
    def post(self, request, article_id):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            request.user.save()
            serializer.save(user=request.user, article_id=article_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    # 댓글 수정
    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            serializer = CommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({"message":"댓글 수정했습니다."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"댓글 작성자만 수정할 수 있습니다."},status=status.HTTP_403_FORBIDDEN)
        
    # 댓글 삭제
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({"message": "댓글을 삭제하였습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "댓글 작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        

# ----- 댓글 반응 -----

class CommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 좋아요
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        try:
            commentreaction = CommentReaction.objects.get(comment=comment, user=user)
        except CommentReaction.DoesNotExist:
            commentreaction = CommentReaction.objects.create(comment=comment, user=user)

        if user in commentreaction.like.all():
            commentreaction.like.remove(user)
            comment.like_count -=1
            comment.save()
            return Response("좋아요를 취소했습니다.", status=status.HTTP_202_ACCEPTED)
        
        elif user in commentreaction.hate.all():
            commentreaction.hate.remove(user)
            commentreaction.like.add(user)
            comment.like_count +=1
            comment.hate_count -=1
            comment.save()
            return Response("싫어요를 취소하고, 좋아요를 했습니다.", status=status.HTTP_201_CREATED)
        
        else:
            commentreaction.like.add(user)
            comment.like_count +=1
            comment.save()
            return Response("좋아요를 했습니다.", status=status.HTTP_200_OK)
 

class CommentHateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 싫어요
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        try:
            commentreaction = CommentReaction.objects.get(comment=comment, user=user)
        except CommentReaction.DoesNotExist:
            commentreaction = CommentReaction.objects.create(comment=comment, user=user)

        if user in commentreaction.hate.all():
            commentreaction.hate.remove(user)
            comment.hate_count -=1
            comment.save()
            return Response("싫어요를 취소했습니다.", status=status.HTTP_202_ACCEPTED)
        
        elif user in commentreaction.like.all():
            commentreaction.like.remove(user)
            commentreaction.hate.add(user)
            comment.hate_count +=1
            comment.like_count -=1
            comment.save()
            return Response("좋아요를 취소하고, 싫어요를 했습니다.", status=status.HTTP_201_CREATED)
        
        else:
            commentreaction.hate.add(user)
            comment.hate_count +=1
            comment.save()
            return Response("싫어요를 했습니다.", status=status.HTTP_200_OK)
    
# ----- 댓글 끝 -----