from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views

urlpatterns = [
    path('user/token/', api_views.NewTokenObtainPairView.as_view(), name="token"),
    path('user/registrar/', api_views.RegisterView.as_view(), name="registrar"),
    path('user/token/refresh/', TokenRefreshView.as_view(),name="refresh"),
    path('user/profile/<user_id>', api_views.ProfileView.as_view(), name="profile"),
    path('user/password-reset/<email>/', api_views.PasswordEmailVerify.as_view(), name='password_reset'),
    path('user/password-change/', api_views.PasswordChangeView.as_view(), name='password_reset'),

    # Endpoint p/ post

    path('posts/categoria/lista/', api_views.CategoryListAPIView.as_view(), name="lista-categorias"),
    path('posts/categoria/<category_slug>', api_views.PostCategoryListAPIView.as_view(), name="categoria"),
    path('posts/lista/', api_views.PostListAPIView.as_view(), name="lista-posts"),
    path('posts/post/<slug>', api_views.PostDetailAPIView.as_view(), name="post"),
    path('posts/like-post/', api_views.LikePostAPIView.as_view(), name="post-like"),
    path('posts/comentario-post/', api_views.PostComentarioAPIView.as_view(), name="post-comment"),
    path('posts/favorito-post/', api_views.PostBookmarkAPIView.as_view(), name="post-bookmark"),

    # Endpoint p/ dashboard

    path('autor/dashboard/estatisticas/<user_id>', api_views.DashboardStatsAPIView.as_view(), name="dashboard"),
    path('autor/dashboard/lista-comentarios/<user_id>', api_views.DashboardComentarioLists.as_view(), name="dashboard-comentarios"),
    path('autor/dashboard/lista-posts/', api_views.DashboardPostLists.as_view(), name="dashboard-posts"),
    path('autor/dashboard/lista-notificacoes/<user_id>', api_views.DashboardNotificacaoLists.as_view(), name="dashboard-notificacoes"),
    path('autor/dashboard/notificacao-vista', api_views.DashboardNotificacaoVista.as_view(), name="dashboard-notificacao-vista"),
    path('autor/dashboard/resposta-comentario/', api_views.DashboardRespostaComentarioAPIView.as_view(), name="dashboard-resposta"),
    path('autor/dashboard/criar-post/', api_views.DashboardPostAPIVIew.as_view(), name="dashboard-post"),
    path('autor/dashboard/atualizar-post/<user_id>/<post_id>/', api_views.DashboardEditarPostAPIView.as_view(), name="dashboard-post-edit"),
]