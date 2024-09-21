from django.contrib import admin
from api import models as api_models

admin.site.register(api_models.User)
admin.site.register(api_models.Profile)
admin.site.register(api_models.Categoria)
admin.site.register(api_models.Post)
admin.site.register(api_models.Notificacao)
admin.site.register(api_models.Comentario)
admin.site.register(api_models.Bookmark)
