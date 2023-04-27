from django.contrib import admin

from .models import Post, Transaction

admin.site.register(Post)
admin.site.register(Transaction)