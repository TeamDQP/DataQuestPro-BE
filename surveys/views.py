from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from .models import Survey, Category, Tag, Question, Answer
from .serializers import SurveySerializer, CategorySerializer, TagSerializer, QuestionSerializer, AnswerSerializer

# Create your views here.
### Survey
class SurveyCreate(APIView):

    def post(self, request):
        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)  # 현재 로그인한 사용자를 Survey의 user 필드에 연결
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class SurveyDetail(APIView):

    def get(self,request, pk):
        try:
            survey = Survey.objects.select_related('question_set', 'tag_set').get(pk=pk)
        except Survey.DoesNotExist:
            return Response({"error": "설문이 존재하지 않습니다"}, status=404)

        questions = survey.question_set.prefetch_related(
            Prefetch('answer_set', queryset=Answer.objects.select_related('question'))
        ).all()

        serialized_questions = QuestionSerializer(questions, many=True).data
        serialized_tags = TagSerializer(survey.tag_set.all(), many=True).data
        data = {
            "title":"survey",
            "survey_id":pk,
            "survey":survey,
            "questions":serialized_questions,
            "tags":serialized_tags
        }
        return Response(data)


class SurveyDelete(APIView):

    def post(self, request, pk):
        try:
            survey_to_delete = Survey.objects.get(pk=pk)
            survey_to_delete.delete()
            return Response({"message": "설문 삭제가 완료되었습니다"}, status=200)
        except Survey.DoesNotExist:
            return Response({"message": "삭제하려는 설문이 존재하지 않습니다"}, status=404)
    

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