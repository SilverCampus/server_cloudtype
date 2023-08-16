from django.urls import path, include
from .views import *

urlpatterns = [
    path('search-courses/', search_courses, name='search-courses'),               # 1번, api 문서 Ok
    path('course/<int:course_id>/video/', CourseVideoListView.as_view(), name="CourseVideoList"),     # 2번, api 문서 Ok
    path('course-enroll/', course_enroll, name='course-enroll'),                  # 3번, api 문서 Ok
    path('purchased-courses/', purchased_courses, name='purchased-courses'),      # 4번, api 문서 Ok
    path('course-like/', course_like, name='course-like'),                        # 5번, api 문서 Ok
    path('liked-courses/', liked_courses, name='liked-courses'),                  # 6번, api 문서 Ok
    path('launch-course/', launch_course, name="launch-course"),                  # 7번, api 문서 Ok
    path('video-upload/', video_upload, name='video-upload'),                     # 8번, api 문서 Ok
    path('ask-question/', ask_question, name='ask-question'),                     # 9번, api 문서 Ok
    path('answer-question/', answer_question, name='answer-question'),            # 10번, api 문서 Ok
    path('update-course-description/', update_course_description, name='update-course-description'),    # 11번,
    path('get-course-videos/', get_course_videos, name='get-course-videos'),      # 12번, api 문서 Ok
    # path('get-recently-watched-courses/', get_recently_watched_courses, name='get-recently-watched-courses'),    # 13번, 
    # path('recently-liked-course/', recently_liked_course, name='recently-liked-course'),     # 14번, api 문서 Ok
    path('get-user-courses/', get_user_courses, name='get-user-courses'), # 13, 합친 뷰
    path('video-completion/', video_completion, name='video-completion'),         # 14번, api 문서 Ok
    path('basic-cource-info/', basic_cource_info, name='basic-cource-info'),      # 15번, api 문서 Ok
    path('get-course-list-completion-rate/', get_course_list_completion_rate, name='get-course-list-completion-rate'), # 16번, api 문서 Ok
    path('get-question-list/', get_question_list, name='get-question-list'),      # 17번, api 문서 Ok
    path('get-question-detail/', get_question_detail, name='get-question-detail'), # 18번,
    path('get-user-info/', get_user_info, name='get-user-info'), # 19번,
] 