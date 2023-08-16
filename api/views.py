from campus.models import *
from campus.serializers import (UserSerializer, SearchCoursesSerializer, 
                                CourseVideoListSerializer, PurchasedCoursesSerializer, 
                                EnrollSerializer, LikeSerializer, LikedCoursesSerializer,
                                LaunchCourseSerializer, VideoUploadSerializer, AskQuestionSerializer,
                                AnswerQuestionSerializer, CourseDescriptionUpdateSerializer,
                                GetCourseVideoSerializer, LikedCoursesSerializer,
                                GetRecentlyWatchedCoursesSerializer, CourseSerializer,
                                VideoCompletionSerializer, GetQuestionListSerializer, 
                                GetQuestionDetailSerializer, GetCourseListCompletionRateSerializer,
                                GetUserInfoSerializer, BasicCourceInfoSerializer)

from rest_framework.generics import ListAPIView, CreateAPIView

from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

import boto3
from django.conf import settings

from django.utils import timezone


# 1. 특정 검색어를 입력하거나, 특정 카테고리의 이름을 쿼리 파라미터로 전달하면 관련된 강좌들 클라이언트에게 보내주는 API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_courses(request):
    keyword = request.GET.get('keyword') # 쿼리 파라미터로 전달받아야 함!
    user = request.user
    
    if keyword is None:
        return Response({"message": "Keyword is required"}, status=status.HTTP_400_BAD_REQUEST)

    courses = Course.objects.filter(title__icontains=keyword)
    courses_list = list(courses)

    try:
        category = Category.objects.get(name=keyword)
        related_courses = category.course.all()
        courses_list.extend(related_courses)
    except Category.DoesNotExist:
        # 카테고리가 없을 경우에 대한 처리는 필요에 따라 작성
        pass

    # 중복 제거
    courses_set = set(courses_list)

    if not courses_set:
        return Response({"message": "검색 결과가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 찾은 객체들을 시리얼라이즈
    serializer = SearchCoursesSerializer(list(courses_set), many=True, context={'user': user})
    return Response(serializer.data, status=status.HTTP_200_OK)


# 2. Course와 연결된 Video list 반환하는 API (GET)
class CourseVideoListView(ListAPIView):
    serializer_class = CourseVideoListSerializer

    # list 수정하지 않아도, get_queryset() 함수만 오버라이딩 해도 충분!
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Video.objects.filter(course__id = course_id)


# 3. 로그인한 사용자가 특정 강좌를 구매(등록)하는 API
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def course_enroll(request):
    user = request.user

    # if user.is_instructor: # User가 강사라면
    #     return Response({"error": "User is Instructor"}, status=status.HTTP_400_BAD_REQUEST)

    course_id = request.data.get('course_id')  # request.data가 request.POST보다 일반적

    if not course_id:
        return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
    
    enroll, created = Enroll.objects.get_or_create( # created: 객체가 새로 생성되었으면 True, 기존에 존재했으면 False   
        user = user,                                                          
        course = course
    )

    if created: # 해당 객체가 지금 처음 생성된 것이라면
        enroll.save()  # DB에 저장
    else:
        return Response({"error": "This enroll already exists"}, status=status.HTTP_400_BAD_REQUEST) # 중복 저장 막는 예외처리

    # 응답을 위한 Serializer를 사용합니다.
    serializer = EnrollSerializer(enroll)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 4. 로그인한 사용자가 구매한 강좌 목록들 반환하는 API
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) #로그인한 사용자만 접근 가능
def purchased_courses(request):
    user = request.user # 로그인한 사용자 객체 얻기
    enrolls = Enroll.objects.filter(user=user)

    courses = [enroll.course for enroll in enrolls]
    serializer = PurchasedCoursesSerializer(courses, many=True, context={'request': request}) # request를 context로 전달해줘야 함!
                                                                    # Serializer에서 self.context['request']를 사용하고 있기 때문에
    return Response(serializer.data, status=status.HTTP_200_OK)


# 5. 로그인한 사용자가 특정 강좌를 찜하는 API
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def course_like(request):
    course_id = request.data.get('course_id')   # request.POST에서 request.data로 수정!
    if not course_id:
        return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
    # 사용자가 로그인한 상태이므로 request.user에서 사용자 정보를 가져옵니다.
    user = request.user

    try:
        like = Like.objects.get(user=user, course=course)
    except ObjectDoesNotExist:
        # Enroll 객체를 생성합니다.
        like = Like(
            course=course, user=user
        )
        # DB에 저장합니다.
        like.save()
        # 응답을 위한 Serializer를 사용합니다.
        serializer = LikeSerializer(like)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    like.delete()  # 이렇게 하면 객체 사라져??
    return Response({"data": "기존 찜 취소 함 ㅋ"}, status=status.HTTP_200_OK)

    


# 6. 로그인한 사용자가 찜한 강좌 목록들 반환하는 API
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) # 로그인한 사용자만 접근 가능
def liked_courses(request):
    user = request.user # 로그인한 사용자 객체 얻기
    likes = Like.objects.filter(user=user)

    courses = [like.course for like in likes]
    serializer = LikedCoursesSerializer(courses, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


# 7. 로그인한 사용자(강사)가 새로운 강좌를 개설하는 하는 API
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def launch_course(request):
    user = request.user

    if not user.is_instructor: # User가 강사가 아니라면
        return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)

    # 전달받은 데이터 추출
    title = request.data.get('title')
    price = request.data.get('price')
    description = request.data.get('description')
    category_name = request.data.get('category_name')  # 프론트엔드로부터 이름으로 받음. id x
    # thumbnail = request.data.get('thumbnail')   
    thumbnail = request.FILES.get('thumbnail') # 나중에 S3에 저장하는 로직대로 처리해야!!
    is_live = request.data.get('is_live')
    credits = request.data.get('credits') # 몇 학점짜리 수업인지 
    
    # 카테고리 객체 찾기 (예외 처리를 위해 get_object_or_404를 사용할 수도 있음)
    try:
        category = Category.objects.get(name=category_name)
    except ObjectDoesNotExist:
        return Response({"error": "Category does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    

    # S3 연결
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    # 파일 경로 지정
    file_path = 'images/' + str(thumbnail)

    # S3에 업로드
    s3_client.upload_fileobj(thumbnail, settings.AWS_STORAGE_BUCKET_NAME, file_path, ExtraArgs={'ContentType': 'image/jpeg'})

    # S3 URL 생성
    thumbnail_url = f'{file_path}'

    course = Course(
        title=title,
        price=price,
        description=description,
        instructor=user,  # 강좌의 강사는 현재 로그인해 있는 User
        category=category,
        thumbnail=thumbnail_url,
        is_live=is_live,
        credits=credits
    )
    course.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = LaunchCourseSerializer(course)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 8. 강사가 자신이 개설한 강좌에 새로운 영상 파일을 추가하는 API 
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def video_upload(request):  
    user = request.user

    if not user.is_instructor: # User가 강사가 아니라면
        return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 프론트엔드로부터 넘겨받는 정보: title, video_file, course(id)
    title = request.data.get('title')
    video_file = request.FILES.get('video_file')  # 여길 나중에 FILES로 바꿔야!!
    # video_file = request.data.get('video_file')
    course_id = request.data.get('course_id')

    try: # 해당 강좌 뽑아 오기
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "There is no Course"}, status=status.HTTP_400_BAD_REQUEST)

    if course.instructor != user:
        return Response({"error": "Unmatched btw instructor and course"}, status=status.HTTP_400_BAD_REQUEST)

    # order_in_course 값 확보하기 (추가 함!)
    order_in_course = course.video_count() + 1

    # S3 연결
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    # 파일 경로 지정
    file_path = 'videos/' + str(video_file)

    # S3에 업로드
    s3_client.upload_fileobj(video_file, settings.AWS_STORAGE_BUCKET_NAME, file_path, ExtraArgs={'ContentType': 'video/mp4'})

    # S3 URL 생성
    video_url = f'{file_path}'

    video = Video(
        title=title,
        video_file=video_url,
        course=course,
        order_in_course = order_in_course
    )
    video.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = VideoUploadSerializer(video)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    

# 9. 로그인한 학생이 자신이 수강 중인 강좌에 대해 question 등록하는 API
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def ask_question(request):
    user = request.user

    # if user.is_instructor: # User가 강사라면 -> 예외처리
    #     return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)

    # 프론트엔드로부터 넘겨받는 정보: title, content, course(id)
    title = request.data.get('title')
    content = request.data.get('content')
    course_id = request.data.get('course_id')

    try: # 해당 강좌 뽑아 오기
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "there is no Course"}, status=status.HTTP_400_BAD_REQUEST)
    
    try: # 해당 학생이 넘겨받은 수업 듣고 있는지 체크 -> 아니면 예외처리
        enroll_check = Enroll.objects.get(course=course, user=user)
    except Enroll.DoesNotExist:
        return Response({"error": "User did not enroll this course"}, status=status.HTTP_400_BAD_REQUEST)

    question = Question(
        title = title,
        content = content,
        student = user,
        course = course
    )
    question.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = AskQuestionSerializer(question)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 10. 로그인한 선생님이 자신이 개설한 강좌에 대한 question에 comment를 달아주는 API
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def answer_question(request):   # 프론트로부터 넘겨 받아야 할 정보: question_id, content(답글 내용)
    user = request.user

    if not user.is_instructor: # User가 강사가 아니라면 -> 예외처리
        return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)
    
    question_id = request.data.get('question_id')
    content = request.data.get('content')

    # 해당 질문 객체 뽑아 오기
    try:
        question = Question.objects.get(id=question_id)
    except ObjectDoesNotExist:
        return Response({"error": "There is no that question"}, status=status.HTTP_400_BAD_REQUEST)

    course = question.course  # 해당 질문을 참조하여 강좌 객체 가져오기!

    # 해당 강좌가 현재 로그인한 강사의 강좌가 아닐 때 -> 예외처리
    if course.instructor != user: 
        return Response({"error": "This course is not current Instructor's"}, status=status.HTTP_400_BAD_REQUEST)
    
    comment = Comment(
        content = content,
        instructor = user,
        question = question
    )
    comment.save()

    # Serializer를 사용해 JSON 응답 생성
    serializer = AnswerQuestionSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    


# 11. 로그인한 선생님이 자신의 강좌의 description을 수정하는 API (정연)
@api_view(['PATCH'])
@permission_classes((permissions.IsAuthenticated,)) # course_id를 url로 받음
def update_course_description(request): # 프론트로부터 넘겨 받아야 할 정보: course_id, content(description 내용)
    user = request.user
    course_id = request.data.get('course_id')

    if not user.is_instructor: # User가 강사가 아니라면 -> 예외처리
            return Response({"error": "User is not Instructor"}, status=status.HTTP_400_BAD_REQUEST)
    
    # course_id에 대해 course 객체 받아오기
    try:
        course = Course.objects.get(id=course_id, instructor=user)
    except Course.DoesNotExist: 
        return Response({"error": "Course not found or you are not the instructor."}, status=404)

    # 해당 강좌가 현재 로그인한 강사의 강좌가 아닐 때 -> 예외처리
    if course.instructor != user: 
        return Response({"error": "This course is not current Instructor's"}, status=status.HTTP_400_BAD_REQUEST)
    
    description = request.data.get('description')  # 프론트엔드에서 전달한 description 값 추출
    title = course.title
    price = course.price
    category = course.category
    thumbnail = course.thumbnail
    is_live = course.is_live
    credits = course.credits
    
    if description is not None:
        course = Course(
            id = course_id,
            description = description,
            title = title,
            price = price,
            instructor = user,
            category = category,
            thumbnail = thumbnail,
            is_live = is_live,
            credits = credits
        ) # description 값 업데이트

        course.save()

    serializer = CourseDescriptionUpdateSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 12. 로그인한 수강자가 자신이 구매한 강좌에 대한 강의들을 시청할 수 있도록 특정 강의 영상을 불러오는 API
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_course_videos(request):
    user = request.user
    course_id = request.GET.get('course_id')
    order_in_course = request.GET.get('order_in_course')

    try:
        enroll = Enroll.objects.get(user=user, course_id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "This Enroll not found."}, status=404)
    
    try:
        video = Video.objects.get(course_id=course_id, order_in_course=order_in_course)
    except ObjectDoesNotExist:
        return Response({"error": "This video not found."}, status=404)
    
    try:
        course = Course.objects.get(id = course_id)
    except ObjectDoesNotExist:
        return Response({"error": "There is no Course"}, status=404)

    # 해당 강좌의 전체 비디오 목록에서 현재 비디오를 제외함
    videos = Video.objects.filter(course_id=course_id).exclude(id=video.id).order_by('order_in_course')
    
    recentlyWatched, created = RecentlyWatched.objects.get_or_create(user=user, course=course)

    if not created:
        recentlyWatched.watched_at = timezone.now()
        recentlyWatched.save()
    
    # 강의 및 전체 비디오 정보를 시리얼라이즈
    video_serializer = GetCourseVideoSerializer(video)
    videos_serializer = GetCourseVideoSerializer(videos, many=True)
    
    # 특정 강의 정보와 전체 비디오 목록을 함께 반환
    response_data = {
        'current_video': video_serializer.data,
        'else_videos': videos_serializer.data
    }
    return Response(response_data, status=status.HTTP_200_OK)


# # 13. 로그인한 수강자가 가장 최근에 수강한 강좌를 불러오는 API (정연)
# @api_view(['GET'])
# @permission_classes((permissions.IsAuthenticated,))
# def get_recently_watched_courses(request):
#     user = request.user
#     recently_watched = RecentlyWatched.objects.filter(user=user).order_by('-watched_at')

#     if user.is_instructor: # User가 강사라면 에러
#         return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)
    
#     # 가장 최근에 시청한 강좌 id를 first_course_id에 저장
#     if recently_watched:
#         first_course_id = recently_watched[0].course_id
#     else:
#         return Response({}, status=200)
    
#     # first_course_id에 해당하는 course를 response
#     try:
#         course = Course.objects.get(id=first_course_id)
#     except Course.DoesNotExist: 
#         return Response({"error": "Course not found."}, status=404)
    
#     serializer = GetRecentlyWatchedCoursesSerializer(course, many=False) 
#     return Response(serializer.data, status=status.HTTP_200_OK)


# # 14. 로그인한 수강자의 가장 최근에 찜한 강의를 반환해주는 API (규빈)
# @api_view(['GET'])
# @permission_classes((permissions.IsAuthenticated,)) 
# def recently_liked_course(request):
#     # 사용자가 좋아요를 누른 강의 중 가장 최근 것을 가져옴
#     recent_liked = Like.objects.filter(user=request.user).order_by('-id').first()

#     # 만약 찜한 강의가 없으면 빈 응답을 반환
#     if not recent_liked:
#         return Response({"detail": "No recent liked course found."}, status=404)

#     course = recent_liked.course
#     serializer = CourseSerializer(course)

#     return Response(serializer.data)


# 13. 로그인한 수강자의 가장 최근 수강한 강좌와 가장 최근 찜한 강좌 각각 반환
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_user_courses(request):
    user = request.user

    if user.is_instructor:
        return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)

    # 최근에 시청한 강좌를 가져옴
    recently_watched = RecentlyWatched.objects.filter(user=user).order_by('-watched_at')
    first_course_id = recently_watched[0].course_id if recently_watched else None

    try:
        recently_watched_course = Course.objects.get(id=first_course_id) if first_course_id else None
    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=404)

    # 최근에 좋아요를 누른 강의를 가져옴
    recent_liked = Like.objects.filter(user=request.user).order_by('-id').first()
    recently_liked_course = recent_liked.course if recent_liked else None

    # 두 강좌를 직렬화
    watched_serializer = GetRecentlyWatchedCoursesSerializer(recently_watched_course, many=False) if recently_watched_course else None
    liked_serializer = CourseSerializer(recently_liked_course) if recently_liked_course else None

    # 함께 응답을 반환
    response_data = {
        "recently_watched": watched_serializer.data if watched_serializer else None,
        "recently_liked": liked_serializer.data if liked_serializer else None,
    }

    return Response(response_data, status=status.HTTP_200_OK)


# 14. 로그인한 수강자가 특정 강좌의 특정 강의에 대한 수강 완료 체크하는 API (POST)
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,)) # 프론트로부터 받아야할 것들: course_id, order_in_course 
def video_completion(request):
    user = request.user
    course_id = request.data.get('course_id')
    order_in_course = request.data.get('order_in_course')

    # if user.is_instructor:  # User가 강사라면 -> 예외처리
    #     return Response({"error": "User is not Student"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:  # 해당 강좌 뽑아 오기
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"error": "there is no Course"}, status=status.HTTP_400_BAD_REQUEST)

    try:  # 해당 학생이 넘겨받은 강좌를 듣고 있는지 체크 -> 아니면 예외처리
        enroll_check = Enroll.objects.get(course=course, user=user)
    except Enroll.DoesNotExist:
        return Response({"error": "User did not enroll this course"}, status=status.HTTP_400_BAD_REQUEST)

    # 해당 강좌에 order_in_course 가 있는지 체크 -> 아니면 예외처리
    if int(course.video_count()) < int(order_in_course): # 에러!
        return Response({"error": "This order_in_course is invalid!"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        video = Video.objects.get(course_id=course_id, order_in_course=order_in_course) # 일치하는 비디오 객체 반환

    videoCompletion, created = VideoCompletion.objects.get_or_create( # videoCompletion: 검색되거나, 새로 생성된 객체 가르키는 변수          
        user = user,                                                  # created: 객체가 새로 생성되었으면 True, 기존에 존재했으면 False
        video = video
    )

    if created: # 새로 생성이 된 것이면
        videoCompletion.save()  # VideoCompletion 객체 생성 후 저장

        # 여기에서 User의 total_credits을 업데이트하고, 이 업데이트 결과에 따라서 등급을 결정하도록 수정하기!!
        completion_rate = course.completion_rate(user)
        if completion_rate == 100:
            user.total_credits += course.credits    
            user.save()  # 그리고 저장!!

            user.update_grade()

    # Serializer를 사용해 JSON 응답 생성
    serializer = VideoCompletionSerializer(videoCompletion)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 15. 구매 여부와 상관없이 특정 한 강좌에 대한 기본 정보를 반환하는 API(GET)
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def basic_cource_info(request): # 쿼리 파라미터로 받아야 할 정보: course_id
    
    # is_this_instructor True False로 반환해주는거 반영, 그리고 해당 유저가
    # 저 강의 찜 했는지 안 했는지 체크 하는 것도 넣어야!
    course_id = request.GET.get('course_id')
    user = request.user

    try:
        course = Course.objects.get(id = course_id)
    except ObjectDoesNotExist:
        return Response({"error": "there is no Course"}, status=status.HTTP_400_BAD_REQUEST)
    
        # Serializer를 사용해 JSON 응답 생성
    serializer = BasicCourceInfoSerializer(course, context={'user': user})
    return Response(serializer.data, status=status.HTTP_200_OK)


# 16. 수강자가 구매한 강좌의 비디오 리스트 수강여부와 해당 강좌 수강률 반환하는 API (GET)
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) 
def get_course_list_completion_rate(request): # 쿼리 파라미터로 받아야 할 정보: course_id
    user = request.user
    course_id = request.GET.get('course_id')

    try: # 해당 강좌가 있는지 체크
        course = Course.objects.get(id = course_id)
    except ObjectDoesNotExist:
        return Response({"error": "there is no Course"}, status=status.HTTP_400_BAD_REQUEST)
    
    try: # 해당 user가 이 강의를 수강하고 있는지 체크
        enroll = Enroll.objects.get(course_id = course_id, user = user)
    except ObjectDoesNotExist:
        return Response({"error": "The User does not enroll the Course"}, status=status.HTTP_400_BAD_REQUEST)
    
    video_list = course.video.all() # 역참조로 course와 연결된 비디오들 다 가져오기
    
    # 수강률을 계산하기 위해 completion_rate 메서드를 사용
    completion_rate = course.completion_rate(user)

    # 각 비디오가 수강 완료되었는지 여부 넣어서 확인
    video_completion_data = []
    for video in video_list:

        serializer = GetCourseListCompletionRateSerializer(video, context={'user': user})
        video_completion_data.append(serializer.data)

    # 수강률과 비디오 수강 완료 정보를 반환
    response_data = {
        "completion_rate": completion_rate,  # 수강률
        "videos": video_completion_data      # 각 비디오 별 수강 확인
    }

    return Response(response_data, status=status.HTTP_200_OK)


# 17. 한 강좌에 연결되어있는 Question 리스트 반환 (GET)
@api_view(['GET'])
def get_question_list(request):
    course_id = request.GET.get('course_id')

    if course_id is None:
        return Response({"message": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    question_list = Question.objects.filter(course_id=course_id)

    if not question_list:
        return Response({"data": None}, status=status.HTTP_200_OK)  # 클라이언트 요청 반영하여 수정

    serializer = GetQuestionListSerializer(question_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 18. 한 question 객체에 대한 상세 정보 반환 + 해당 Question에 연결된 comment들까지 같이 반환
@api_view(['GET'])
def get_question_detail(request):
    question_id = request.GET.get('question_id') # 쿼리파라미터로 넘겨주기 

    try:
        question_detail = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({"error": "There is no such question"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = GetQuestionDetailSerializer(question_detail)

    return Response(serializer.data)

# 19번 access 토큰을 바탕으로 해당 유저 정보 반환해주는 뷰
@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,)) 
def get_user_info(request):
    user = request.user
    
    serializer = GetUserInfoSerializer(user)

    return Response(serializer.data, status=200)

    
    
    


    

