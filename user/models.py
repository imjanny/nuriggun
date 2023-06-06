from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.urls import reverse


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
    INTEREST = {
        ('it/과학' , 'it'),
        ('경제','economy'),
        ('생활/문화','culture'),
        ('세계','wrold'),
        ('날씨','weather')
    }

    email = models.EmailField("이메일", max_length=25, unique=True, null=False, blank=False)
    password = models.CharField("비밀번호", max_length=25)
    nickname = models.CharField("닉네임", max_length=8,null=True, blank=True)
    interest = models.CharField("관심분야", max_length=20, choices=INTEREST)
    profile_img = models.ImageField("프로필 이미지", blank=True, upload_to="profile/%Y/%m/")
    # subscibe = models.ManyToManyField("self", symmetrical=False, related_name="subscribe", blank=True)
    is_admin = models.BooleanField("관리자",default=False)
    is_active = models.BooleanField("활성화",default=True)
    is_staff = models.BooleanField("스태프",default=False)
    created_at = models.DateTimeField("생성일",auto_now_add=True)
    updated_at = models.DateTimeField("수정일",auto_now=True)

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