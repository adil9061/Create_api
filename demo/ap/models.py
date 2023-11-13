from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Images', null=True, blank=True)
    school_name = models.CharField(max_length=150, blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class Live(models.Model):
    title = models.CharField(max_length=150)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    teacher_name = models.CharField(max_length=100)
    batch = models.CharField(max_length=10)
    link = models.URLField()
    status = models.CharField(max_length=30, default="Upcoming Live")
    image = models.ImageField(upload_to='Images')

    def __str__(self):
        return self.title

class Exam(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    mark_per_question = models.IntegerField()
    negative_mark = models.IntegerField()
    total_mark = models.IntegerField()
    status = models.CharField(max_length=20, default='Unattended')
    completed_by = models.ManyToManyField(User, related_name='completed_exams', blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
        return self.text

    
class Attended(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choices = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(null=False, blank=False, default=False)


    def __str__(self):
        return self.exam.title
    
