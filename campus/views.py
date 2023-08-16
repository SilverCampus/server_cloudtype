from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import *
from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegisterSerializer


User = get_user_model()

# 회원가입
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    
# 로그인
class CustomTokenObtainPairView(TokenObtainPairView):
    pass  

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# class InstructorViewSet(ModelViewSet):
#     queryset = Instructor.objects.all()
#     serializer_class = InstructorSerializer

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class VideoViewSet(ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class EnrollViewSet(ModelViewSet):
    queryset = Enroll.objects.all()
    serializer_class = EnrollSerializer

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer                   

class RecentlyWatchedViewSet(ModelViewSet):
    queryset = RecentlyWatched.objects.all()
    serializer_class = RecentlyWatchedSerializer




