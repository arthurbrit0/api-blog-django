from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views

urlpatterns = [
    path('user/token/', api_views.NewTokenObtainPairView.as_view()),
    path('user/registrar/', api_views.RegisterView.as_view()),
    path('user/token/refresh/', TokenRefreshView.as_view()),
    path('user/profile/<user_id>', api_views.ProfileView.as_view()),

    # Endpoint p/ post

    path('posts/categoria/lista/', api_views.CategoryListAPIView.as_view()),
    path('posts/categoria/posts/<category_slug>', api_views.PostCategoryListAPIView.as_view()),
    path('posts/listas/', api_views.PostListAPIView.as_view()),
    path('posts/post/<slug>', api_views.PostDetailAPIView.as_view()),
]