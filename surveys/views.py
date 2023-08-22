from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db.models import Prefetch
from .models import Survey, Category, Tag, Question, Answer
from .serializers import SurveySerializer, CategorySerializer, TagSerializer, QuestionSerializer, AnswerSerializer

# Create your views here.
### Survey
class SurveyCreate(APIView):

    def post(self, request):
        survey_serializer = SurveySerializer(data=request.data)
        if survey_serializer.is_valid():
            survey_instance = survey_serializer.save(user=self.request.user)
            
            questions_data = request.data.get('questions')
            
            for question_data in questions_data:
                question_data['survey'] = survey_instance.id
                question_serializer = QuestionSerializer(data=question_data)
                if question_serializer.is_valid():
                    question_instance = question_serializer.save()
                    answer_data = question_data.get('answers')
                    for answer_text in answer_data:
                        answer_serializer = AnswerSerializer(data={'question': question_instance.id, 'answer_text': answer_text})
                        if answer_serializer.is_valid():
                            answer_serializer.save()
                        else:
                            return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(survey_serializer.data, status=status.HTTP_201_CREATED)
        return Response(survey_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurveyDetail(APIView):

    def get(self, request, pk):
        try:
            survey = Survey.objects.select_related('category', 'user').prefetch_related('question_set__answer_set').get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"error": "설문이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

        questions = survey.question_set.all()
        serialized_questions = QuestionSerializer(questions, many=True).data

        answers = Answer.objects.filter(question__survey=survey)
        serialized_answers = AnswerSerializer(answers, many=True).data

        data = {
            "title": "survey",
            "survey_id": pk,
            "survey": SurveySerializer(survey).data,
            "questions": serialized_questions,
            "answers": serialized_answers,
            "tags": TagSerializer(survey.tags.all(), many=True).data
        }
        return Response(data)


class SurveyDelete(APIView):

    def post(self, request, pk):

        survey_to_delete = get_object_or_404(Survey, pk=pk, created_by=request.user)

        password = request.data.get("password")

        user = authenticate(username=request.user.username, password=password)
        
        if not user:
            return Response({"message": "비밀번호가 일치하지 않습니다"}, status=400)
        
        survey_to_delete.delete()
        return Response({"message": "설문 삭제가 완료되었습니다"}, status=200)
    

class SurveyUpdate(APIView):

    def post(self, request, pk):
        try:
            survey_instance = Survey.objects.get(pk=pk)
        except Survey.DoesNotExist:
            return Response({"message": "업데이트할 설문이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SurveySerializer(survey_instance, data=request.data)

        if serializer.is_valid():
            updated_survey = serializer.save()

            questions_data = request.data.get('questions')
            if questions_data:
                for question_data in questions_data:
                    question_id = question_data.get('id')
                    if question_id:
                        question_instance = Question.objects.get(id=question_id)
                        question_serializer = QuestionSerializer(question_instance, data=question_data)
                        if question_serializer.is_valid():
                            question_serializer.save()
                        else:
                            return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        question_data['survey'] = updated_survey.id
                        question_serializer = QuestionSerializer(data=question_data)
                        if question_serializer.is_valid():
                            question_serializer.save()
                        else:
                            return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            answers_data = request.data.get('answers')
            if answers_data:
                for answer_data in answers_data:
                    answer_id = answer_data.get('id')
                    if answer_id:
                        answer_instance = Answer.objects.get(id=answer_id)
                        answer_serializer = AnswerSerializer(answer_instance, data=answer_data)
                        if answer_serializer.is_valid():
                            answer_serializer.save()
                        else:
                            return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        answer_data['question'] = updated_survey.question_set.get(id=answer_data['question']).id
                        answer_serializer = AnswerSerializer(data=answer_data)
                        if answer_serializer.is_valid():
                            answer_serializer.save()
                        else:
                            return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

### category
class CategoryCreate(APIView):

    def post(slef, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

### Tag
class TagCreate(APIView):

    def post(slef, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)