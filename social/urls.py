from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views

router = DefaultRouter()
router.register('posts', BoardPostViewSet)
router.register('comments', BoardCommentViewSet)
router.register('likes', BoardPostLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-post-details/', get_post_details, name='get-post-details'),
    path('add-comment/', views.add_comment, name='add_comment'),
    path('add-like/', views.add_like, name='add_like'),
    path('post-upload/', post_upload, name='post_upload'),
    path('hashtags/', hashtag_list, name='hashtag-list'), 
    path('posts/tag/<str:hashtag_name>/', views.posts_by_hashtag, name='posts-by-hashtag'),
    path('my-posts/', views.my_posts, name='my-posts'),

]

