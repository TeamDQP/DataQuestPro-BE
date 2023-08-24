from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from .models import Survey, Category, Tag, Question, AnswerOption
from .serializers import SurveySerializer, CategorySerializer, TagSerializer, QuestionSerializer, AnswerOptionSerializer

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
                    question_serializer.save()
                else:
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(survey_serializer.data, status=status.HTTP_201_CREATED)
        return Response(survey_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurveyDetail(APIView):

    def get(self,request, pk):
        try:
            survey = Survey.objects.select_related('question_set', 'tag_set').get(pk=pk)
        except Survey.DoesNotExist:
            return Response({"error": "설문이 존재하지 않습니다"}, status=404)

        questions = survey.question_set.prefetch_related(
            Prefetch('answeroption_set', queryset=AnswerOption.objects.select_related('question'))
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
    

class SurveyUpdate(APIView):

    def post(self, request, pk):
        try:
            survey_instance = Survey.objects.get(pk=pk)
        except Survey.DoesNotExist:
            return Response({"message": "업데이트할 설문이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SurveySerializer(survey_instance, data=request.data)

        if serializer.is_valid():
            # 설문 업데이트
            updated_survey = serializer.save()

            # 질문 데이터 처리
            questions_data = request.data.get('questions')
            if questions_data:
                for question_data in questions_data:
                    question_id = question_data.get('id')  # 질문의 기존 ID를 가져옴 (기존 질문 업데이트용)
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