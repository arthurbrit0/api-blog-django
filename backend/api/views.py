from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Sum
# Restframework
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

# Outros
import json
import random

# Imports customizados
from api import serializer as api_serializer
from api import models as api_models

class NewTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.NewTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = api_models.User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.ProfileSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        profile = api_models.Profile.objects.get(user=user)
        return profile
    
class CategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Categoria.objects.all()
    
class PostCategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = api_models.Categoria.objects.get(slug=category_slug)
        posts = api_models.Post.objects.filter(categoria=category, status="Ativo")
        return posts
    
class PostListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Post.objects.filter(status="Ativo")
    
class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs['slug']
        post = api_models.Post.objects.get(slug=slug, status="Ativo")
        post.view += 1
        post.save()
        return post

class LikePostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )

    def post(self,request):
        user_id = request.data['user_id']
        post_id = request.data['post_id']

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"message": "Post descurtido"}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)

            api_models.Notificacao.objects.create(
                user=post.user,
                post=post,
                tipo="Like",
            )
            return Response({"message": "Post curtido"}, status=status.HTTP_201_CREATED)
        
class PostComentarioAPIView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'comment': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )

    def post(self, request):
        post_id = request.data['post_id']
        nome_user = request.data['name']
        email = request.data['email']
        comentario = request.data['comment']

        post = api_models.Post.objects.get(id=post_id)
        api_models.Comentario.objects.create(
            post=post,
            nome_user=nome_user,
            email=email,
            comentario=comentario
        )

        api_models.Notificacao.objects.create(
            user=post.user,
            post=post,
            tipo="Comentario",
        )

        return Response({"message":"Comentário feito"}, status=status.HTTP_201_CREATED)
    
class PostBookmarkAPIView(APIView):
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        post_id = request.data['post_id']
        user_id = request.data['user_id']

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)
        bookmark = api_models.Bookmark.objects.filter(post=post, user=user).first()

        if bookmark:
            bookmark.delete()
            return Response({"message":"Post desfavoritado"}, status=status.HTTP_200_OK)
        else:
            api_models.Bookmark.objects.create(
                user = user,
                post = post,
            )
            return Response({"message":"Post favoritado"}, status=status.HTTP_201_CREATED)
        
def generate_numeric_otp(length=7):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

class PasswordEmailVerify(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = api_serializer.UserSerializer
    
    def get_object(self):
        email = self.kwargs['email']
        user = api_models.User.objects.get(email=email)
        
        if user:
            user.otp = generate_numeric_otp()
            uidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            reset_token = str(refresh.access_token)
            user.reset_token = reset_token
            user.save()

            link = f"http://localhost:5173/create-new-password?otp={user.otp}&uidb64={uidb64}&reset_token={reset_token}"
            
            merge_data = {
                'link': link, 
                'username': user.username, 
            }
            subject = f"Password Reset Request"
            text_body = render_to_string("email/password_reset.txt", merge_data)
            html_body = render_to_string("email/password_reset.html", merge_data)
            
            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[user.email], body=text_body
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
        return user
    

class PasswordChangeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = api_serializer.UserSerializer
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        
        otp = payload['otp']
        uidb64 = payload['uidb64']
        password = payload['password']

        

        user = api_models.User.objects.get(id=uidb64, otp=otp)
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()
            
            return Response( {"message": "Password Changed Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response( {"message": "An Error Occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Views para o Dashboard

class DashboardStatsAPIView(generics.ListAPIView):
    serializer_class = api_serializer.AuthorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)

        views = api_models.Post.objects.filter(user=user).aggregate(view = Sum("view"))['view']
        posts = api_models.Post.objects.filter(user=user).count()
        likes = api_models.Post.objects.filter(user=user).aggregate(total_likes = Sum("likes"))['total_likes']
        bookmarks = api_models.Bookmark.objects.filter(post__user = user).count()

        return [{
            "views": views,
            "posts": posts,
            "likes": likes,
            "bookmarks": bookmarks,
        }]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class DashboardPostLists(generics.ListAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Post.objects.filter(user=user).order_by("-id")
    
class DashboardComentarioLists(generics.ListAPIView):
    serializer_class = api_serializer.ComentarioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)

        comentarios = api_models.Comentario.objects.filter(post__user=user)
        return comentarios
    
class DashboardNotificacaoLists(generics.ListAPIView):
    serialzier_class = api_serializer.NotificacaoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        notificacoes = api_models.Notificacao.objects.filter(seen=False, user=user)

class DashboardNotificacaoVista(APIView):
    def post(self, request):
        id_notificacao = request.data['noti_id']
        notificacao = api_models.Notificacao.objects.get(id=id_notificacao)

        notificacao.seen=True
        notificacao.save()
        return Response({"message":"Notificação marcada como vista"}, status=status.HTTP_200_OK)
    
class DashboardRespostaComentarioAPIView(APIView):
    def post(self, request):
        id_comentario = request.data['comment_id']
        resposta = request.data['resposta']

        comentario = api_models.Comentario.objects.get(id=id_comentario)
        comentario.resposta = resposta
        comentario.save()

        return Response({"message":"Resposta do comentário enviada"}, status=status.HTTP_201_CREATED)
    
class DashboardPostAPIVIew(generics.CreateAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        id_user = request.data.get("user_id")
        titulo = request.data.get("titulo")
        imagem = request.data.get("imagem")
        descricao = request.data.get("descricao")
        tags = request.data.get("tags")
        id_categoria = request.data.get("categoria")
        post_status = request.data.get("post_status")

        user = api_models.User.objects.get(id=id_user)
        categoria = api_models.Categoria.objects.get(id=id_categoria)

        api_models.Post.objects.create(
            user=user,
            titulo = titulo,
            imagem = imagem,
            descricao = descricao,
            tags = tags,
            categoria=categoria,
            status = post_status,
        )

        return Response({"message":"Post criado com sucesso"}, status=status.HTTP_201_CREATED)
    
class DashboardEditarPostAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        post_id = self.kwargs['post_id']

        user = api_models.User.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id, user=user)
        return post
    
    def update(self, request, *args, **kwargs):
        instancia_post = self.get_object()

        titulo = request.data.get("titulo")
        imagem = request.data.get("imagem")
        descricao = request.data.get("descricao")
        tags = request.data.get("tags")
        id_categoria = request.data.get("categoria")
        post_status = request.data.get("post_status")

        categoria = api_models.Categoria.objects.get(id=id_categoria)

        instancia_post.titulo = titulo
        if imagem != "undefined":
            instancia_post.imagem = imagem
        instancia_post.descricao = descricao
        instancia_post.tags = tags
        instancia_post.categoria = categoria
        instancia_post.status = post_status
        instancia_post.save()

        return Response({"message":"Post atualizado com sucesso"}, status=status.HTTP_200_OK)