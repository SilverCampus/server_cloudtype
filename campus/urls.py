from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegisterView, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'category', CategoryViewSet)
# router.register(r'instructor', InstructorViewSet)
router.register(r'course', CourseViewSet)
router.register(r'video', VideoViewSet)
router.register(r'like', LikeViewSet)
router.register(r'enroll', EnrollViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'question', QuestionViewSet)
router.register(r'recentlywatched',RecentlyWatchedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='user-register'),            # 회원가입 Api 문서 Ok
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인 Api 문서 Ok
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),       # access token 리프레쉬 Api 문서 Ok
]

