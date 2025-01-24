from django.contrib import admin

from api.models import User
from api.models import Post ,Comment
# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)