from rest_framework import serializers
from .models import BoardPost, BoardComment, BoardPostLike, Hashtag
from campus.models import User
from django.core.exceptions import ObjectDoesNotExist

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ('id', 'name')

class BoardPostSerializer(serializers.ModelSerializer):

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
    # comment_user = AuthorSerializer(source='user', read_only=True)
    class Meta:
        model = BoardComment
        fields = ('comment_user', 'content', 'created_at')

class PostUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPost
        fields = '__all__'


class PostsByHashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = '__all__'




class GetAllBoardPostsSerializer(serializers.ModelSerializer):
    hashtag_name = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    user_grade = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()


    class Meta:
        model = BoardPost
        fields = ['id', 'user_name', 'user_grade', 'content', 'video', 'video_thumbnail', 'created_at', 'hashtag_name', 'is_liked']
        

    def get_hashtag_name(self, obj):
        return obj.hashtags.name
    
    def get_is_liked(self, obj):
        user = self.context.get('user')
        try: 
            boardpostlike = BoardPostLike.objects.get(user=user, post=obj)
        except ObjectDoesNotExist:
            return False
        
        return True         
    
    def get_user_name(self, obj):
        user = obj.user
        return user.nickname
    
    def get_user_grade(self, obj):
        user = obj.user
        return user.grade