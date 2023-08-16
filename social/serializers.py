from rest_framework import serializers
from .models import BoardPost, BoardComment, BoardPostLike, Hashtag
from campus.models import User

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ('id', 'name')

class BoardPostSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True)

    class Meta:
        model = BoardPost
        fields = '__all__'

class BoardCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardComment
        fields = '__all__'

class BoardPostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPostLike
        fields = '__all__'

####### 특정 API에 대한 view 만들 때 쓰는 별도 시리얼라이즈들 ########
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'grade')

class PostCommentSerializer(serializers.ModelSerializer):
    comment_user = AuthorSerializer(source='user', read_only=True)
    class Meta:
        model = BoardComment
        fields = ('comment_user', 'content', 'created_at')

class PostUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPost
        fields = '__all__'