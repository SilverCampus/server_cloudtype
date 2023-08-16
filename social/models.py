from django.db import models
from campus.models import User

class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class BoardPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='social_posts/images/', null=True, blank=True)  
    video = models.FileField(upload_to='social_posts/videos/', null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='social_posts/thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, related_name='posts')

    def __str__(self):
        return self.title

class BoardComment(models.Model):
    post = models.ForeignKey(BoardPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20] + "..."

class BoardPostLike(models.Model):
    post = models.ForeignKey(BoardPost, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']

    def __str__(self):
        return f"{self.user.username}의 좋아요"
