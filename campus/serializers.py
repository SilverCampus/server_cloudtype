from rest_framework import serializers
from django.contrib.auth import get_user_model
from campus.models import Course, Category, Video, Like, Enroll, Comment, Question, User, RecentlyWatched, VideoCompletion
from django.core.exceptions import ObjectDoesNotExist

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # password = serializers.CharField(write_only=True) 코드를 추가하는 이유는 
    # 패스워드 필드에 대해 특별한 처리를 하기 위해서. 그 처리가 바로 write_only=True 인데, 
    # 이 설정이 있으면 시리얼라이저는 해당 필드를 "쓰기 전용"으로 만든다.
    # 일반적으로 사용자 정보를 클라이언트에게 반환할 때 패스워드와 같은 민감한 정보를 포함해서는 안 되기에 
    # write_only=True 설정을 사용하면, 해당 필드는 클라이언트에서 서버로의 요청(request)에만 사용되고, 
    # 서버에서 클라이언트로의 응답(response)에는 포함되지 않게 된다.
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'address', 'phone', 'birth_date', 'nickname', 'is_instructor')

    def create(self, validated_data):
        # User는 password 해싱을 자동으로 처리해서 저장해주도록
        # User.objects.create_user() 방식으로 객체를 생성함!(다른 객체 생성과 달리)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            address=validated_data.get('address', ''),
            phone=validated_data.get('phone', ''),
            birth_date=validated_data.get('birth_date'),
            nickname=validated_data.get('nickname', ''),
            is_instructor=validated_data.get('is_instructor', True) # is_instructor 필드 추가
        )
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    video_count = serializers.SerializerMethodField() # video_count 필드 추가
    instructor = serializers.SerializerMethodField()
    # is_this_instructor = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'description', 'instructor', 'category', 'thumbnail', 'is_live', 'video_count', 'credits'] # video_count 필드를 포함
        
    def get_video_count(self, obj):
        return obj.video.count() # obj는 현재 Course 인스턴스입니다. video_count 메서드를 호출해 개수를 반환합니다.

    def get_instructor(self, obj):
        return obj.instructor.nickname

class BasicCourceInfoSerializer(serializers.ModelSerializer):
    
    video_count = serializers.SerializerMethodField() # video_count 필드 추가
    instructor = serializers.SerializerMethodField()
    is_this_instructor = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'description', 'instructor', 'category', 'thumbnail', 'is_live', 'video_count', 'credits', 'is_this_instructor', 'is_liked']

    def get_video_count(self, obj):
        return obj.video.count() # obj는 현재 Course 인스턴스입니다. video_count 메서드를 호출해 개수를 반환합니다.

    def get_instructor(self, obj):
        return obj.instructor.nickname
    
    def get_is_this_instructor(self, obj):
        user = self.context.get('user')
        
        if obj.instructor == user:
            return True
        else:
            return False
        
    def get_is_liked(self, obj):
        user = self.context.get('user')
        course = obj

        try:
            Like.objects.get(user = user, course=course)
        except ObjectDoesNotExist:
            return False
        
        return True


class GetCourseListCompletionRateSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id','title', 'video_file', 'course', 'order_in_course', 'completed']

    def get_completed(self, obj):
        user = self.context.get('user')
        video_id = obj.id
        try:
            videocompletion = VideoCompletion.objects.get(user=user, video_id=video_id)
        except ObjectDoesNotExist:
            return False
        return True


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class RecentlyWatchedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentlyWatched
        fields = '__all__'       


class VideoCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model =VideoCompletion
        fields = '__all__'


#######  api 앱 내에서 view 만들 때 쓰는 별도 시리얼라이즈들 ########

# class UserRegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'

class SearchCoursesSerializer(serializers.ModelSerializer):
    video_count = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()   
    is_liked = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'description', 'instructor', 'category', 'thumbnail', 'is_live', 'video_count', 'credits', 'is_liked'] # video_count 필드를 포함

    def get_video_count(self, obj):
        return obj.video.count() # obj는 현재 Course 인스턴스입니다. video_count 메서드를 호출해 개수를 반환합니다.

    def get_instructor(self, obj):
        return obj.instructor.nickname
    
    def get_is_liked(self, obj):
        user = self.context.get('user')
        course = obj

        try:
            Like.objects.get(user = user, course=course)
        except ObjectDoesNotExist:
            return False
        
        return True




class CourseVideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'  

class PurchasedCoursesSerializer(serializers.ModelSerializer):
    video_count = serializers.SerializerMethodField() # video_count 시리얼라이즈 필드 추가
    completion_rate = serializers.SerializerMethodField() # completion_rate 시리얼라이즈 필드 추가
    instructor = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'description', 'instructor', 'category', 'thumbnail', 'is_live', 'video_count', 'credits', 'completion_rate'] 
        # video_count, completion_rate 시리얼라이즈 필드 포함

    def get_video_count(self, obj):
        return obj.video.count() # obj는 현재 Course 인스턴스입니다. video_count 메서드를 호출해 개수를 반환합니다.     
    
    def get_completion_rate(self, obj):
        user = self.context['request'].user  # 현재 로그인해 있는 사람의 정보를 가져옴!!
        return obj.completion_rate(user)
    
    def get_instructor(self, obj):
        return obj.instructor.nickname

class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class LikedCoursesSerializer(serializers.ModelSerializer):
    video_count = serializers.SerializerMethodField() # video_count 필드 추가
    instructor = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'description', 'instructor', 'category', 'thumbnail', 'is_live', 'video_count', 'credits'] # video_count 필드를 포함

    def get_video_count(self, obj):
        return obj.video.count() # obj는 현재 Course 인스턴스입니다. video_count 메서드를 호출해 개수를 반환합니다.

    def get_instructor(self, obj):
        return obj.instructor.nickname

class LaunchCourseSerializer(serializers.ModelSerializer):
    video_count = serializers.SerializerMethodField() # video_count 필드 추가
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'description', 'instructor', 'category', 'thumbnail', 'is_live', 'video_count', 'credits'] # video_count 필드를 포함
    
    def get_video_count(self, obj):
        return obj.video.count() # obj는 현재 Course 인스턴스입니다. video_count 메서드를 호출해 개수를 반환합니다.               


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class AskQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'        


class AnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class CourseDescriptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class GetCourseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class GetRecentlyWatchedCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class VideoCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCompletion
        fields = '__all__'


class GetQuestionListSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField() # nickname 필드 추가
    class Meta:
        model = Question
        fields  = ['id', 'nickname', 'title']

    def get_nickname(self, obj):
        return obj.student.nickname

class QuestionCommentSerializer(serializers.ModelSerializer):
    instructor_nickname = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['content', 'question', 'instructor_nickname']

    def get_instructor_nickname(self, obj):
        return obj.instructor.nickname


class GetQuestionDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField() # comments 필드 추가
    student_nickname = serializers.SerializerMethodField() # comments 필드 추가
    course_name = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'student_nickname', 'course_name', 'comments']

    def get_comments(self, obj):
        comments = Comment.objects.filter(question=obj)
        return QuestionCommentSerializer(comments, many=True).data  

    def get_student_nickname(self, obj):
        return obj.student.nickname
    
    def get_course_name(self, obj):
        return obj.course.title
    
class GetUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'is_instructor', 'total_credits', 'grade']
        
        


