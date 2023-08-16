from rest_framework import viewsets
from .models import BoardPost, BoardComment, BoardPostLike, Hashtag
from .serializers import (
    BoardPostSerializer, BoardCommentSerializer, BoardPostLikeSerializer, AuthorSerializer, PostCommentSerializer,
    PostUploadSerializer, HashtagSerializer)
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from campus.models import User
from moviepy.editor import VideoFileClip
import os
from django.core.files import File
from django.core.files.base import ContentFile
from rest_framework.generics import ListAPIView


class BoardPostViewSet(viewsets.ModelViewSet):
    queryset = BoardPost.objects.all()
    serializer_class = BoardPostSerializer

class BoardCommentViewSet(viewsets.ModelViewSet):
    queryset = BoardComment.objects.all()
    serializer_class = BoardCommentSerializer

class BoardPostLikeViewSet(viewsets.ModelViewSet):
    queryset = BoardPostLike.objects.all()
    serializer_class = BoardPostLikeSerializer

# 1. 특정 게시물 페이지 API
# 게시물 사진, 게시물 내용, 작성자명, 댓글, 좋아요 수 반환
# 프론트로부터 넘겨 받아야 할 정보: post_id
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_post_details(request):
    post_id = request.GET.get('post_id')

    # 특정 post 정보 뽑아오기
    try:
        post = BoardPost.objects.get(id=post_id)
    except BoardPost.DoesNotExist:
        return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

    # 특정 post에 대한 댓글, 좋아요 정보 뽑아오기 
    comments = BoardComment.objects.filter(post=post)
    likes = BoardPostLike.objects.filter(post=post)

    # 게시글 작성자 정보 가져오기
    author_serializer = AuthorSerializer(post.user)
    comments_serializer = PostCommentSerializer(comments, many=True)
    likes_count = likes.count()
    
    # 해시태그 정보 가져오기
    hashtags_serializer = HashtagSerializer(post.hashtags.all(), many=True)
    
    post_data = BoardPostSerializer(post).data
    post_data['author'] = author_serializer.data
    post_data['comments'] = comments_serializer.data
    post_data['likes'] = likes_count
    post_data['hashtags'] = hashtags_serializer.data
    
    return Response(post_data, status=status.HTTP_200_OK)


# 2. 댓글 추가 비동기 API
# 댓글 추가, 새로고침 안되도록
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def add_comment(request):
    post_id = request.data.get('post_id')
    content = request.data.get('content')
    
    post = BoardPost.objects.get(id=post_id)
    
    comment = BoardComment(post=post, user=request.user, content=content)
    comment.save()
    
    serializer = BoardCommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# 3. 좋아요 추가 비동기 API
# 좋아요 추가, 새로고침 안되도록
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def add_like(request):
    post_id = request.data.get('post_id')
    
    post = BoardPost.objects.get(id=post_id)
    
    if BoardPostLike.objects.filter(post=post, user=request.user).exists():
        return Response({'detail': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
    
    like = BoardPostLike(post=post, user=request.user)
    like.save()
    
    serializer = BoardPostLikeSerializer(like)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# 4. 로그인한 사용자가 새로운 게시글을 게시하는 API
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def post_upload(request):
    user = request.user

    # 프론트엔드로부터 넘겨받는 정보: title, content, image_file, video_file, hashtags
    title = request.data.get('title')
    content = request.data.get('content')
    image_file = request.FILES.get('image_file')
    video_file = request.FILES.get('video_file')
    hashtag_ids = request.data.get('hashtags', [])

    # 게시물 저장
    post = BoardPost(
        user = user,
        title = title,
        content = content,
        image = image_file,
        video = video_file,
    )
    post.save() # 이곳에서 먼저 저장해야 ManyToMany 관계가 정상적으로 작동합니다.

    # 해시태그 연결
    for hashtag_id in hashtag_ids:
        try:
            hashtag = Hashtag.objects.get(id=hashtag_id)
            post.hashtags.add(hashtag)
        except Hashtag.DoesNotExist:
            pass  # 존재하지 않는 해시태그 ID인 경우 무시

    # 영상에서 썸네일 생성
    if video_file:
        with VideoFileClip(video_file.temporary_file_path()) as clip:
            thumbnail_path = os.path.join("/tmp", f"thumb_{os.path.basename(video_file.name)}.png")
            clip.save_frame(thumbnail_path, t=1.00)  # 1초 지점의 프레임 저장

            with open(thumbnail_path, 'rb') as thumb_file:
                # 썸네일을 Django의 FileField로 변환하여 저장
                post.image.save(f"thumb_{video_file.name}.png", ContentFile(thumb_file.read()))
                os.remove(thumbnail_path)  # 임시 썸네일 파일 삭제

    post.save()

    serializer = PostUploadSerializer(post)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

## 5. hashtag 리스트 불러오는 api
@api_view(['GET'])
def hashtag_list(request):
    hashtags = Hashtag.objects.all()
    serializer = HashtagSerializer(hashtags, many=True)
    return Response(serializer.data)

## 6. hashtag 필터링
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def posts_by_hashtag(request, hashtag_name):
    posts = BoardPost.objects.filter(hashtags__name=hashtag_name)
    serializer = BoardPostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
# 7. 로그인한 사용자가 작성한 글을 가져오는 API
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def my_posts(request):
    user = request.user
    posts = BoardPost.objects.filter(user=user).order_by('-created_at')  # 최신글부터 가져오기 위해 '-created_at' 사용
    serializer = BoardPostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
