from rest_framework.views import APIView
from ap.serializers import *
from  rest_framework.response import Response
from ap.models import *
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from rest_framework import generics
from django.utils import timezone
from rest_framework import status
from datetime import datetime
from rest_framework import authentication, permissions
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
import json



# Create your views here.

# For registration

class Register(APIView):
    def post(self, request):
        serializers = UserSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data)

# For Login 

class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed("User not found..!!")

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password..!!')
        current_time = datetime.utcnow()
        payload = { 
            'id' : user.id,
            'iat' : current_time
        }
        
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        new_token = Token(user=user, token=token)
        new_token.save()

        response = Response()
           
        response.set_cookie(key='jwt', value=token)
        response.data = {
            'jwt' : token
        }

        return response

# For view the user

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated....!!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)

# For Create Profile

class ProfileCreate(APIView):
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# For Edit Profile

class EditProfile(APIView):
    def put(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# For Viewing Profile

class ProfilelView(APIView):
    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

# For Create Live

class LiveCreate(APIView):
    def post(self, request):
        serializer = LiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# For List the Live

class LiveList(APIView):
    def get(self, request):
        current_time = timezone.now()
        status = request.query_params.get('filter', 'all')

        if status == 'upcoming':
            live= Live.objects.filter(start_time__gt=current_time)
        elif status == 'ongoing':
            live = Live.objects.filter(start_time__lte=current_time, end_time__gte=current_time)
        elif status == 'completed':
            live = Live.objects.filter(end_time__lt=current_time)
        else:
            live = Live.objects.all()

        for event in live:
            if event.start_time > current_time:
                event.status = 'Upcoming Live'
            elif event.start_time <= current_time and event.end_time >= current_time:
                event.status = 'Ongoing Live'
            else:
                event.status = 'Live Completed'
            event.save()

        serializer = LiveSerializer(live, many=True)
        response_data = {
            'live': serializer.data,
        }

        return Response(response_data)

# For Create Exam

class CreateExam(APIView):
    def post(self, request):
        serializer = ExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# List Unattended Exam 

class UnattendedExamList(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        print(token)
        if not token:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user_id = payload['id']  # Assuming your payload has a 'user_id' field
            current_user = User.objects.get(id=user_id)
            print(current_user)
            print(user_id)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated....!!')

        current_time = timezone.now()
        unattended_exams = Exam.objects.filter(start_time__gt=current_time)

        for exam in unattended_exams:
            exam.status = 'Unattended'
            exam.save()

        serializer = ExamSerializer(unattended_exams, many=True)
        response_data = {
            'unattended': serializer.data,
        }

        return Response(response_data)

# List Completed Exam

class CompletedExamList(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        print(token)
        if not token:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user_id = payload['id']
            current_user = User.objects.get(id=user_id)


        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated....!!')

        current_time = timezone.now()
        completed_exams = Exam.objects.filter(end_time__lt=current_time, status='Completed')

        for exam in completed_exams:
            exam.status = 'Completed'
            exam.save()

        serializer = ExamSerializer(completed_exams, many=True)
        response_data = {
            'completed': serializer.data,
        }

        return Response(response_data)

class ExamView(APIView):
    def get(self, request, exam_id):

        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user_id = payload['id']  # Assuming your payload has a 'user_id' field
            current_user = User.objects.get(id=user_id)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            exam = Exam.objects.get(pk=exam_id)

            # Check if the exam has not started yet
            current_time = timezone.now()
            if exam.start_time and current_time <= exam.start_time:
                return Response({"message": "Exam has not started yet."}, status=status.HTTP_403_FORBIDDEN)

            start_time = timezone.localtime(exam.start_time) if exam.start_time else None
            end_time = timezone.localtime(exam.end_time) if exam.end_time else None

            # if exam.status != 'Completed':
            #     # Update the status to 'Completed' for the current user
            #     exam.status = 'Completed'
            #     exam.save()
            # print(f"Exam status after update: {exam.status}")


            exam_data = {
                "current_user": current_user.username,
                "title": exam.title,
                "start_time": start_time,
                "end_time": end_time,
                "mark_per_question": exam.mark_per_question,
                "negative_mark": exam.negative_mark,
                "total_mark": exam.total_mark,
                "status": exam.status
            }

            return Response(exam_data)
        except Exam.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CreateQuestion(APIView):
    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CreateChoices(APIView):
    def post(self, request):
        serializer = ChoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ListQuestions(APIView):
    def get(self, request, exam_id):

        # Filter questions related to the specified exam
        questions = Question.objects.filter(exam_id=exam_id)
        data = []

        exam = Exam.objects.get(pk=exam_id)

        if exam.start_time and exam.end_time:
            current_time = timezone.now()
            remaining_time = exam.end_time - current_time

            if current_time >= exam.start_time and remaining_time.total_seconds() > 0:

                remaining_time = timedelta(seconds=remaining_time.total_seconds())

                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                duration_str = f"{hours} HH, {minutes} MM, {seconds} SS"
                data.append({'duration': duration_str})

        for question in questions:
            question_data = QuestionSerializer(question).data
            choices_data = [ChoiceSerializer(choice).data for choice in question.choices.all()]
            question_data['choices'] = choices_data
            data.append(question_data)

        return Response(data)

class CheckAnswer(APIView):
    def post(self, request, question_id):

        token = request.COOKIES.get('jwt')
        print(token)
        if not token:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated....!!')

        user = User.objects.get(id=payload["id"])

        mutable_data = request.data.copy()
        mutable_data['user'] = user.id

        serializer = AttendedSerializer(data=mutable_data)

        if serializer.is_valid():
            try:
                question = Question.objects.get(id=question_id)
                print(question)
            except Question.DoesNotExist:
                return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

            choices = serializer.validated_data['choices']
            print(choices)

            is_correct = choices.is_correct

            # Check if the question and choices are associated
            if question != choices.question:
                return Response({"error": "Question and choices do not match"}, status=status.HTTP_400_BAD_REQUEST)
            demo = choices.question
            print(demo)
            serializer.validated_data['is_correct'] = is_correct
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AttendedAnswer(APIView):
    
    def get(self, request, exam_id):

        token = request.COOKIES.get('jwt')
        print(token)
        if not token:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated....!!')

        user = User.objects.get(id=payload["id"])

        print(user)
        exam = Exam.objects.get(pk=exam_id)

        duration_str = "Not applicable"
        if exam.start_time and exam.end_time:
            current_time = timezone.now()
            remaining_time = exam.end_time - current_time

            if current_time >= exam.start_time and remaining_time.total_seconds() > 0:
                # Convert remaining_time to a timedelta object
                remaining_time = timedelta(seconds=remaining_time.total_seconds())

                # Extract hours, minutes, and seconds from the timedelta
                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                duration_str = f"{hours} HH, {minutes} MM, {seconds} SS"

        exam_data = {
            "mark_per_question": exam.mark_per_question,
            "negative_mark": exam.negative_mark
        }

        duration = exam.end_time - exam.start_time

        questions = Question.objects.filter(exam_id=exam_id)
        data = []  # Initialize the data list here

        correct_answers_count = 0
        wrong_answers_count = 0
        unattended_questions_count = 0

        for question in questions:
            question_data = QuestionSerializer(question).data
            choices_data = [ChoiceSerializer(choice).data for choice in question.choices.all()]
            question_data['choices'] = choices_data

            # Check if any choice for this question is marked as correct
            # has_correct_choice = any(choice['is_correct'] for choice in choices_data)
            
            attended_questions = Attended.objects.filter(exam=exam, question=question, user=user)

            if attended_questions.exists():
                # Handle the case when there is at least one attended question
                attended_question = attended_questions.first()  # You may want to define a logic to choose one if there are multiple
                if attended_question.is_correct:
                    correct_answers_count += 1
                else:
                    wrong_answers_count += 1
            else:
                # Handle the case when no attended question is found
                unattended_questions_count += 1


            data.append(question_data)
        
        question_count = len(data)
        
        response_data = {

            "duration": str(duration),
            "Time_Remaining" : duration_str,
            "Total_Count": question_count,
            "Correct_count" : correct_answers_count,
            "wrong_count" : wrong_answers_count,
            "unattended_count" : unattended_questions_count,
            "exam_data": exam_data,
            "questions": data,
        }
        return Response(response_data)



class Result(APIView):

    def get(self, request, exam_id):

        token = request.COOKIES.get('jwt')
        print(token)
        if not token:
            raise AuthenticationFailed('Unauthenticated....!!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated....!!')

        user = User.objects.get(id=payload["id"])

        exam = Exam.objects.get(pk=exam_id)
        exam.start_time = timezone.localtime(exam.start_time) if exam.start_time else None
        exam.end_time = timezone.localtime(exam.end_time) if exam.end_time else None


        exam_data = {
            "mark_per_question": exam.mark_per_question,
            "negative_mark": exam.negative_mark,
            "Total_Mark" : exam.total_mark,
            "Started" : exam.start_time,
            "Ended" : exam.end_time
        }

        correct_answers_count = 0
        wrong_answers_count = 0
        unattended_questions_count = 0

        questions = Question.objects.filter(exam_id=exam_id)

        for question in questions:
            choices_data = [ChoiceSerializer(choice).data for choice in question.choices.all()]

            attended_questions = Attended.objects.filter(exam=exam, question=question, user=user)

            if attended_questions.exists():
                # Handle the case when there is at least one attended question
                attended_question = attended_questions.first()  # You may want to define a logic to choose one if there are multiple
                if attended_question.is_correct:
                    correct_answers_count += 1
                else:
                    wrong_answers_count += 1
            else:
                # Handle the case when no attended question is found
                unattended_questions_count += 1

        question_count = len(questions)

        your_score = (correct_answers_count * exam.mark_per_question) + (wrong_answers_count * exam.negative_mark)

        exam.status = 'Completed'
        exam.save()

        response_data = {            
            "username": user.username,
            "exam_data" : exam_data,
            "Correct_count": correct_answers_count,
            "Wrong_count": wrong_answers_count,
            "Unattended_count": unattended_questions_count,
            "Total_count": question_count,
            "Your_Score" : your_score,
        }
        return Response(response_data)



# class ExamList(APIView):
#     def get(self, request):
#         current_time = timezone.now()
#         status = request.query_params.get('filter', 'all')

#         if status == 'unattended':
#             exam = Exam.objects.filter(start_time__gt=current_time)
#         elif status == 'completed':
#             exam = Exam.objects.filter(end_time__lt=current_time)
#         else:
#             exam = Exam.objects.all()

#         for exams in exam:
#             if exams.start_time > current_time:
#                 exams.status = 'Unattended'
#             elif exams.end_time < current_time:
#                 exams.status = 'Completed'
#             exams.duration = exams.end_time - exams.start_time
#             exams.save()
        
#         serializer = ExamSerializer(exam, many=True)
#         response_data = {
#             'exam' : serializer.data,
#         }

#         return Response(response_data)


# For Logout



class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


