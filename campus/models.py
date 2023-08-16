from django.db import models
from django.contrib.auth.models import  AbstractUser

# def validate_unique_nickname(value):
#     if value and User.objects.filter(nickname=value).exists():
#         raise ValidationError('This nickname is already in use.')

# 커스티마이징 한 User
class User(AbstractUser):
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True) # 생일
    nickname = models.CharField(max_length=30, unique=True) # 사용자의 닉네임 validators=[validate_unique_nickname]
    is_instructor = models.BooleanField(default=True)  # 슈퍼 유저 만들 때 자동으로 is_instructor True
    total_credits = models.IntegerField(default=0)  # 총 이수 학점 필드 추가, 초기값은 0

    GRADES = [
        ('Freshman', '새내기'),
        ('Undergraduate', '학부생'), 
        ('Bachelor', '학사'),
        ('Master', '석사'),
        ('Doctorate', '박사'),
        ('Professor', '교수'), 
    ]
    grade = models.CharField(max_length=20, choices=GRADES, default='undergraduate')
    
    def update_grade(self):
        if self.total_credits < 9:
            self.grade = 'Freshman'
        elif self.total_credits < 27:
            self.grade = 'Undergraduate'
        elif self.total_credits < 60:
            self.grade = 'Bachelor'
        elif self.total_credits < 120:
            self.grade = 'Master'
        elif self.total_credits < 180:
            self.grade = 'Doctorate'
        else:
            self.grade = 'Professor' # 180학점 이상 수강하시면 교수!
        self.save()
    

# 카테고리
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# 강좌 릴레이션
class Course(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    instructor = models.ForeignKey(User, related_name='course', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='course' , on_delete=models.CASCADE)
    thumbnail = models.FileField(upload_to='images/') 
    is_live = models.BooleanField(default=False)
    credits = models.PositiveIntegerField() # 1학점, 2학점, 3학점 등을 나타내는 정수 값

    def video_count(self):  # 해당 강좌에 연결된 Video들이 몇 개인지 계산해서 반환해주는 메서드
        return self.video.count() # related_name 'video'를 사용함. 따라서 역참조 할 때 video 이용!
    
    def completion_rate(self, user): # 해당 강좌에 대한 수강자의 수강률을 계산해서 반환해주는 메서드
        total_videos = self.video.count()
        completed_videos = VideoCompletion.objects.filter(user=user, video__course=self).count()
        return (completed_videos / total_videos) * 100 if total_videos > 0 else 0

    def __str__(self):
        return self.title


# 비디오 릴레이션
class Video(models.Model):
    title = models.CharField(max_length=500)
    video_file = models.FileField(upload_to='videos/')  # 실제 영상 파일을 저장할 필드 s3에!!!
    course = models.ForeignKey(Course, related_name='video', on_delete=models.CASCADE)
    order_in_course = models.IntegerField()  # 연결된 강좌 내에서 몇 번째 강의인지 알려주는 속성 

    def __str__(self):
        return self.title


# 좋아요 릴레이션
class Like(models.Model):
    course = models.ForeignKey(Course, related_name='like', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='like', on_delete=models.CASCADE)
    # liked_date = models.DateTimeField(auto_now_add=True) # 새로 추가

    def __str__(self):
        return f"{self.user}의 {self.course}에 대한 좋아요" 


# 등록 릴레이션
class Enroll(models.Model):
    course = models.ForeignKey(Course, related_name='enroll', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='enroll', on_delete=models.CASCADE)
    transaction_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return  f"{self.user}의 {self.course}에 대한 수업 등록"


# 질문 릴레이션
class Question(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    student = models.ForeignKey(User, related_name='question', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='question', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# 답변 릴레이션
class Comment(models.Model):
    content = models.TextField()
    instructor = models.ForeignKey(User, related_name='comment', on_delete=models.CASCADE) 
    question = models.ForeignKey(Question, related_name='comment', on_delete=models.CASCADE)    

    def __str__(self):
        return self.content


# 최근 시청 강좌 저장 릴레이션
class RecentlyWatched(models.Model):
    user = models.ForeignKey(User, related_name='recently_watched', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='recently_watched', on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}이(가) <{self.course.title}>를 ({self.watched_at})에 시청"


# 강의 수강 완료 저장 릴레이션    
class VideoCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}이(가) <{self.video.title}> 강의를 수강 완료"