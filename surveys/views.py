from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import Survey, Category, Tag, Question, AnswerOption, UserAnswer, UserAnswerDetail
from .serializers import SurveySerializer, CategorySerializer, TagSerializer, QuestionSerializer, AnswerOptionSerializer

# Create your views here.
### Survey
class IndexMain(APIView):

    def get(self, request):
        # order by 추가예정
        surveys = Survey.objects.all().select_related('category', 'user')

        processed_surveys = []
        
        for survey in surveys:
            processed_survey = {
                'id': survey.id,
                'user': survey.user.email,
                'title': survey.title,
                'intro': survey.intro,
                'created_at': survey.created_at,
                'updated_at': survey.updated_at,
                'is_done': survey.is_done,
                'category': survey.category.name if survey.category else '',
                'tags': [tag.name for tag in survey.tags.all()],
                'views': survey.views,
            }
            processed_surveys.append(processed_survey)

        return Response(processed_surveys, status=status.HTTP_200_OK)
    

# 테스트 1차 성공
class SurveyCreate(APIView):

    def get(self,request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        # USER 임시 데이터
        user = authenticate(email='test123@gmail.com', password='test123')
        request.data['user'] = user.id
        self.request.user = authenticate(email='test123@gmail.com', password='test123')

        # 태그 데이터 저장
        tags_data = request.data.get('tags')
            
        if tags_data:
            tags = []
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            request.data['tags'] = [tag.id for tag in tags]
            
        survey_serializer = SurveySerializer(data=request.data)

        if survey_serializer.is_valid():
            survey_instance = survey_serializer.save(user=self.request.user)
            
            # 질문 데이터 저장
            questions_data = request.data.get('questions')
            
            for question_data in questions_data:
                question_data['survey'] = survey_instance.id
                question_serializer = QuestionSerializer(data=question_data)
                if question_serializer.is_valid():
                    question_instance = question_serializer.save()
                    answer_data = question_data.get('answers')
                    for answer_text in answer_data:
                        answer_serializer = AnswerOptionSerializer(data={'question': question_instance.id, 'answer_text': answer_text})
                        if answer_serializer.is_valid():
                            answer_serializer.save()
                        else:
                            return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(survey_serializer.data, status=status.HTTP_201_CREATED)
        return Response(survey_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  테스트 1차 테스트 O (데이터 표출)
class SurveyDetail(APIView):

    def get(self, request, pk):
        try:
            survey = Survey.objects.select_related('category', 'user').prefetch_related('question_set__answeroption_set').get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"error": "설문이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)
        
        # 조회수 증가
        survey.views += 1
        survey.save()

        questions = survey.question_set.all()
        serialized_questions = []

        for question in questions:
            serialized_question = QuestionSerializer(question).data
            answer_options = AnswerOption.objects.filter(question=question)
            serialized_question['answer_options'] = [answer.answer_text for answer in answer_options]
            serialized_questions.append(serialized_question)

        data = {
            "title": "survey",
            "survey_id": pk,
            "survey": SurveySerializer(survey).data,
            "category": survey.category.name,
            "questions": serialized_questions,
            "tags": TagSerializer(survey.tags.all(), many=True).data
        }
        return Response(data)


## 테스트 1차 테스트 O
class SurveyDelete(APIView):

    def post(self, request, pk):
        user = authenticate(email='test123@gmail.com', password='test123')

        survey_to_delete = get_object_or_404(Survey, pk=pk, user=user)
        
        if not user:
            return Response({"message": "비밀번호가 일치하지 않습니다"}, status=400)
        
        survey_to_delete.delete()
        return Response({"message": "설문 삭제가 완료되었습니다"}, status=200)
    

## 테스트 1차 테스트 O
class SurveyUpdate(APIView):

    def get(self, request, pk):
        try:
            survey = Survey.objects.select_related('category', 'user').prefetch_related('question_set__answeroption_set').get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"error": "설문이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

        questions = survey.question_set.all()
        serialized_questions = []

        for question in questions:
            serialized_question = QuestionSerializer(question).data
            answer_options = AnswerOption.objects.filter(question=question)
            serialized_question['answer_options'] = [answer.answer_text for answer in answer_options]
            serialized_questions.append(serialized_question)

        categories = Category.objects.all()

        data = {
            "survey_id": pk,
            "survey": SurveySerializer(survey).data,
            "categories": CategorySerializer(categories, many=True).data,
            "questions": serialized_questions,
            "tags": TagSerializer(survey.tags.all(), many=True).data
        }

        return Response(data)
    
    def post(self, request, pk):
        # USER 임시 데이터
        user = authenticate(email='test123@gmail.com', password='test123')
        request.data['user'] = user.id
        self.request.user = authenticate(email='test123@gmail.com', password='test123')

        tags_data = request.data.get('tags')
            
        if tags_data:
            tags = []
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            request.data['tags'] = [tag.id for tag in tags]
            
        survey_instance = get_object_or_404(Survey, pk=pk)
        serializer = SurveySerializer(survey_instance, data=request.data)

        if serializer.is_valid():
            updated_survey = serializer.save()

            # 기존 질문, 답변 데이터 삭제
            updated_survey.useranswer_set.all().delete()
            updated_survey.question_set.all().delete()

            questions_data = request.data.get('questions')
            if questions_data:
                for question_data in questions_data:
                    question_data['survey'] = updated_survey.id
                    question_serializer = QuestionSerializer(data=question_data)
                    if question_serializer.is_valid():
                        question_instance = question_serializer.save()

                        answers_data = question_data.get('answers')
                        if answers_data:
                            for answer_data in answers_data:
                                answer_instance = {'question': question_instance.id, 'answer_text': answer_data}
                                answer_serializer = AnswerOptionSerializer(data=answer_instance)
                                if answer_serializer.is_valid():
                                    answer_serializer.save()
                                else:
                                    return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        
class SurveyResult(APIView):
    def get(self, request, pk):
        try:
            questions = Question.objects.filter(survey_id=pk)
            result = []

            for question in questions:
                answer_options = question.answeroption_set.all()  # 해당 질문에 대한 모든 답변 옵션 가져오기
                question_text = question.question_text

                for answer_option in answer_options:
                    answer_text = answer_option.answer_text
                    answer_count = UserAnswerDetail.objects.filter(
                        useranswer__survey_id=pk,
                        question=question,
                        answer_point=answer_option
                    ).count()

                    result.append({
                        'question_text': question_text,
                        'answer_text': answer_text,
                        'count': answer_count
                    })

            return Response(result, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class UserAnswerView(APIView):
    def post(self, request):
        # Authenticating the user
        user = authenticate(email='test123@gmail.com', password='test123')
        if not user:
            return Response({"error": "Unauthenticated user."}, status=status.HTTP_401_UNAUTHORIZED)
        
        survey_id = request.data.get('survey_id')
        answers = request.data.get('answers', [])

        try:
            survey = Survey.objects.get(pk=survey_id)
        except Survey.DoesNotExist:
            return Response({"error": "Survey does not exist."}, status=status.HTTP_404_NOT_FOUND)

        user_answers = []

        user_answer, created = UserAnswer.objects.get_or_create(
                user=user,
                survey=survey,
            )
        user_answer.save()
        user_answers.append(user_answer)
        
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer_text')

            try:
                question = Question.objects.get(pk=question_id)
            except Question.DoesNotExist:
                continue

            if question.type == "scale":
                try:
                    answer_option = AnswerOption.objects.get(answer_text=answer_text)
                    answer_text = None
                except AnswerOption.DoesNotExist:
                    pass

            if created:
                user_answer_detail = UserAnswerDetail.objects.create(
                    useranswer=user_answer,
                    question=question,
                    answer_point=answer_option,
                    answer_text=answer_text
                )

        return Response({"message": "설문조사 정보가 저장되었습니다."}, status=status.HTTP_201_CREATED)