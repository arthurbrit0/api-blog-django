import shortuuid
from shortuuid.django_fields import ShortUUIDField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.text import slugify

# USuario

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        email_username, domain = self.email.split("@")
        if self.full_name == "" or self.full_name == None:
            self.full_name = email_username
        if self.username == "" or self.username == None:
            self.username = email_username
        
        super(User, self).save(*args, **kwargs)

# Perfil do usuario

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to="image", default="default/default-user.jpg", null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.CharField(max_length=100, null=True, blank=True)
    sobre = models.CharField(max_length=100, null=True, blank=True)
    autor = models.BooleanField(default=False)
    pais = models.CharField(max_length=100, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.user.username

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.full_name
        
        super(Profile, self).save(*args, **kwargs)

def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def salvar_perfil_usuario(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(criar_perfil_usuario, sender=User)
post_save.connect(salvar_perfil_usuario, sender=User)

# Categoria do post

class Categoria(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.FileField(upload_to="image", null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug==None:
            self.slug==slugify(self.titulo)
        super(Categoria, self).save(*args, **kwargs)

    def post_count(self):
        return Post.objects.filter(categoria=self).count()
    
# Post

class Post(models.Model):

    STATUS = (
        ("Ativo", "Ativo"),
        ("Rascunho", "Rascunho"),
        ("Desabilitado", "Desabilitado"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)
    imagem = models.FileField(upload_to="image", null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=100, default="Ativo")
    view = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="likes_user")
    slug = models.SlugField(unique=True, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.titulo
    
    class Meta:
        ordering = ["-data"]
        verbose_name_plural = "Posts"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            self.slug = slugify(self.titulo) + "-" + shortuuid.uuid()[:2]
        
        super(Post, self).save(*args, **kwargs)

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    nome_user = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    comentario = models.TextField(null=True, blank=True)
    resposta = models.TextField(null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.post.titulo
    
    class Meta:
        ordering = ["-data"]
        verbose_name_plural = "Comentarios"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.titulo
    
    class Meta:
        ordering = ["-data"]
        verbose_name_plural = "Bookmarks"

class Notificacao(models.Model):
    TIPO_NOTIFICACAO = (
        ("Like","Like"),
        ("Comentario","Comentario"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tipo = models.CharField(choices=TIPO_NOTIFICACAO, max_length=100)
    visto = models.BooleanField(default=False)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.post:
            return f"{self.post.titulo} - {self.tipo}"
        else:
            return "Notificação"
    
    class Meta:
        ordering = ["-data"]
        verbose_name_plural = "Notificações"



    

    


