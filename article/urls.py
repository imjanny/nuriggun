from django.urls import path, include
from article import views

urlpatterns = [

    path("home/", views.HomeView.as_view(), name="home_view"),
    path("", views.ArticleView.as_view(), name="article_view"),
    path("<int:article_id>/",views.ArticleDetailView.as_view(),name="article_detail_view"),
    path("list/<int:user_id>/", views.ArticleListView.as_view(), name="article_list"),
    path("<int:article_id>/comment/", views.CommentView.as_view(), name="comment_view"), # /article/<int:article_id>/comment/ 댓글(보기/작성)
    path("comment/<int:comment_id>/", views.CommentView.as_view(), name="comment_view"), # /article/<int:article_id>/comment/<int:comment_id>/ 댓글(수정/삭제)
    path("comment/<int:comment_id>/like/", views.CommentLikeView.as_view(), name="comment_like_view"), # /article/comment/<int:comment_id>/like/ 댓글 좋아요
    path("comment/<int:comment_id>/hate/", views.CommentHateView.as_view(), name="comment_hate_view"), # /article/comment/<int:comment_id>/hate/ 댓글 싫어요
    path('scrap/', views.ScrapListView.as_view(),name='scrap_view'),  # 북마크 한 게시글
    path('<int:article_id>/scrap/', views.ScrapView.as_view(),name='scrap_view'),  # 북마크 기능
    path("search/", views.ArticleSearchView.as_view(), name="article_search"), # 검색 기능
    path("<int:article_id>/reaction/", views.ArticleReactionView.as_view(),name="article_reaction"),
    # 카테고리 url
    path("<str:category>/", views.ArticleView.as_view(), name="category_view"),
]


