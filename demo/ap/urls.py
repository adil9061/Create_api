from django.urls import path
from ap import views

urlpatterns = [

    # For User Register, Login, View and Logout

    path('register', views.Register.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('user', views.UserView.as_view(), name='user'),
    path('logout', views.LogoutView.as_view(), name='logout'),

    # For create Profile, View and Edit

    path('create_profile/', views.ProfileCreate.as_view(), name='profile_create'),
    path('profile_view/<int:pk>/', views.ProfilelView.as_view(), name='profile_view'),
    path('edit_profile/<int:pk>/', views.EditProfile.as_view(), name='edit_profile'),

    # For create Live and List it

    path('live/', views.LiveCreate.as_view(), name='live'),
    path('live_list/', views.LiveList.as_view(), name='live-list'),

    # For Create Exam

    path('create_exam/', views.CreateExam.as_view(), name='create_exam'),
    # path('exam_list/', views.ExamList.as_view(), name='exam_list'),
    path('unattended_exam_list/', views.UnattendedExamList.as_view(), name='unattended_exam_list'),
    path('completed_exam_list/', views.CompletedExamList.as_view(), name='completed_exam_list'),
    path('exam_view/<int:exam_id>/', views.ExamView.as_view(), name='exam_view'),

    path('create_question/', views.CreateQuestion.as_view(), name='create_exam'),
    path('create_choices/', views.CreateChoices.as_view(), name='create_choices'),
    path('list-questions/<int:exam_id>/', views.ListQuestions.as_view(), name='list-questions'),

    path('attended_answer/<int:exam_id>/', views.AttendedAnswer.as_view(), name='attended_answer'),

    path('attended/<int:question_id>/', views.CheckAnswer.as_view(), name='attended-list-create'),

]
