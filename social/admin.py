from django.contrib import admin

from .models import BoardPost, BoardComment, BoardPostLike, Hashtag

admin.site.register(BoardPost)
admin.site.register(BoardComment)
admin.site.register(BoardPostLike)
admin.site.register(Hashtag)