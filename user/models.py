from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.urls import reverse
from django.core.mail import EmailMessage


class UserManager(BaseUserManager):

    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        superuser = self.create_user(
            email=email,
            password=password,
        )
        superuser.is_admin = True
        superuser.is_active = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser):
    INTEREST = [
        ('it/과학', 'it'),
        ('경제', 'economy'),
        ('생활/문화', 'culture'),
        ('스포츠', 'sport'),
        ('날씨', 'weather'),
        ('world', 'world')
    ]

    email = models.EmailField("email address", max_length=25, unique=True, null=False, blank=False)
    password = models.CharField("비밀번호", max_length=200)
    nickname = models.CharField("닉네임", max_length=8,null=True, blank=True)
    interest = models.CharField("관심분야", max_length=15, choices=INTEREST, blank=True)
    profile_img = models.ImageField("프로필 이미지", blank=True, upload_to="profile/%Y/%m/")
    subscribe = models.ManyToManyField("self", symmetrical=False, related_name="subscribes", blank=True)
    is_admin = models.BooleanField("관리자",default=False)
    is_active = models.BooleanField("활성화",default=False)
    is_staff = models.BooleanField("스태프",default=False)
    created_at = models.DateTimeField("생성일",auto_now_add=True)
    updated_at = models.DateTimeField("수정일",auto_now=True)
    report_count = models.PositiveIntegerField(default=0)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
        

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_absolute_url(self):
        return reverse('user_profile_view', args=[str(self.id)])

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


# 쪽지 모델


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField("읽음 표시", default=False)

    def __str__(self):
        return self.title
    
#신고 기능
#UniqueConstraint 한번에 한 명의 유저만 신고
class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='report_user')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')

    
      
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "reported_user",], name="unique_report"
            )
        ]


# 이메일 알림 동의
class EmailNotificationSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_notification = models.BooleanField("이메일 알림 동의", default=False)

    def __str__(self):
        return str(self.user.email)