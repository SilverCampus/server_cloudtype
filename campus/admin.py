from django.contrib import admin
from .models import Category, Course, Video, Like, Enroll, Comment, Question, RecentlyWatched, VideoCompletion
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.register(User)
admin.site.register(Category)
# admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(Like)
admin.site.register(Enroll)
admin.site.register(Comment)
admin.site.register(Question)
admin.site.register(RecentlyWatched)
admin.site.register(VideoCompletion)