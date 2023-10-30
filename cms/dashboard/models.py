from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# custom user manager
class MyUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None):
        if not email:
            raise ValueError('User must have a email address')
        if not first_name:
            raise ValueError('User must have a first name')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = MyUserManager()

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
    
class Blog(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=1000)
    description = models.TextField()
    image = models.ImageField(upload_to='blog_image/', null=True, blank=True)
    liked_by = models.ManyToManyField(User, related_name="liked_contents", null=True, blank=True)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    content = models.ForeignKey(Blog, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
