from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views

urlpatterns = [
    path('user/token/', api_views.NewTokenObtainPairView.as_view(), name="token"),
    path('user/registrar/', api_views.RegisterView.as_view(), name="registrar"),
    path('user/token/refresh/', TokenRefreshView.as_view(),name="refresh"),
    path('user/profile/<user_id>', api_views.ProfileView.as_view(), name="profile"),

    # Endpoint p/ post

    path('posts/categoria/lista/', api_views.CategoryListAPIView.as_view(), name="lista-categorias"),
    path('posts/categoria/<category_slug>', api_views.PostCategoryListAPIView.as_view(), name="categoria"),
    path('posts/lista/', api_views.PostListAPIView.as_view(), name="lista-posts"),
    path('posts/post/<slug>', api_views.PostDetailAPIView.as_view(), name="post"),
    path('posts/like-post/', api_views.LikePostAPIView.as_view(), name="post-like"),
    path('posts/comentario-post/', api_views.PostComentarioAPIView.as_view(), name="post-comment"),
    path('posts/favorito-post/', api_views.PostBookmarkAPIView.as_view(), name="post-bookmark"),
]