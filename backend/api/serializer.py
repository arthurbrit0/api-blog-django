from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from api import models as api_models

class NewTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['full_name'] = user.email
        token['username'] = user.username
        return token
    
class RegisterSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    senha_2 = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = api_models.User
        fields = ['full_name','email','senha','senha_2']

    def validate(self, attribute):
        if attribute['senha'] != attribute['senha_2']:
            raise serializers.ValidationError({"senha":"As senhas não conferem."})

        return attribute

    def create(self, validated_data):
        user = api_models.User.objects.create(
            full_name= validated_data['full_name'],
            email= validated_data['email'],
        )

        email_username, domain = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data['senha'])
        user.save()

        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.User
        fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Profile
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    def get_post_count(self, categoria):
        return categoria.posts.count()
    
    class Meta:
        model = api_models.Categoria
        fields = ["id","titulo","imagem","slug","post_count"]

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Comentario
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CommentSerializer, self).__init__(*args,**kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Post
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PostSerializer, self).__init__(*args,**kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Bookmark
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(BookmarkSerializer, self).__init__(*args,**kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Notificacao
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(NotificationSerializer, self).__init__(*args,**kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1

class AuthorSerializer(serializers.Serializer):
    views = serializers.IntegerField(default=0)
    posts = serializers.IntegerField(default=0)
    likes = serializers.IntegerField(default=0)
    bookmarks = serializers.IntegerField(default=0) 