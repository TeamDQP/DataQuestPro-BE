from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import Survey, Category, Tag, Question, AnswerOption, UserAnswer, UserAnswerDetail
from .serializers import SurveySerializer, CategorySerializer, TagSerializer, QuestionSerializer, AnswerOptionSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
### Survey
class IndexMain(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        '''
            설문조사리스트를 불러오는 API

            ---
            # 내용
                -id : 설문조사 PK
                -user: 유저 정보
                -title": 설문 조사 제목
                -intro": 설문 조사 설명
                -created_at": 설문조사 작성시간
                -updated_at": 설문조사 수정시간
                -is_done": 설문조사 활성화상태
                -category": 카테고리 내용
                -tags: 태그 내용
                -views: 설문조사 조회수
                -owner: 설문조사 작성자 확인
                -useranswer: 유저가 해당설문조사에 대한 답변 유무
        '''
        category = request.query_params.get('category')
        surveys = Survey.objects.all().select_related('category', 'user').order_by('-created_at','is_done')

        if category and category != 'all':
            surveys = surveys.filter(category__id=category)

        categories = Category.objects.all()
        processed_surveys = []
        
        for survey in surveys:
            useranswer = UserAnswer.objects.filter(survey=survey, user=request.user)
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
                'owner': True if request.user.email == survey.user.email else False,
                'useranswer': True if useranswer else False,
            }
            processed_surveys.append(processed_survey)
        
        category_serializer = CategorySerializer(categories, many=True)

        data = {
            'surveys': processed_surveys,
            'categories': category_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    

# 테스트 1차 성공
class SurveyCreate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        '''
            설문조사의 포함되는 카테고리리스트 불러오는 API

            ---
            # 내용
                -id : 카테고리 ID
                -name: 카테고리 이름
        '''
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        '''
            설문조사를 저장하는 API

            ---
            # Parameters
                -title : 설문조사 제목
                -intro : 설문조사 설명
                -is_done : 설문조사 활성화상태
                -enddated_at : 설문조사 종료시간
                -questions : 설문조사 내용
                -category : 카테고리 내용
                -tags : 태그 내용
        '''
        # 태그 데이터 저장
        tags_data = request.data.get('tags')
        
        if tags_data:
            tags = []
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            request.data['tags'] = [tag.id for tag in tags]
        
        authentication = JWTAuthentication()
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
        validated_token = authentication.get_validated_token(token)
        
        request.data['user'] = validated_token['user_id']

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
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        '''
            설문조사 내용을 확인하는 API

            ---
            # 내용
                -survey: {
                -    id": 설문조사 PK
                -    title: 설문조사 제목
                -    intro: 설문조사 설명
                -    created_at: 설문조사 작성시간
                -    updated_at: 설문조사 수정시간
                -    enddated_at: 설문조사 종료시간
                -    is_done: 설문조사 활성화상태
                -    views: 설문조사 조회수 
                -    user: 설문조사 작성한 유저
                -    category: 설문조사 카테고리
                -    tags: 설문조사 태그
                -}
                -category: 카테고리 내용
                -questions: 설문조사 질문 예시답변 내용
                -tags: 태그 내용
        '''
        try:
            survey = Survey.objects.select_related('category', 'user').prefetch_related('question_set__answeroption_set').get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"error": "설문이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)
        
        # 조회수 증가
        survey.views += 1
        survey.save()

        questions = survey.question_set.all()
        serialized_questions = []

        if request.user:
            user_answers = UserAnswerDetail.objects.filter(useranswer__survey=survey, useranswer__user=request.user)


        for question in questions:
            serialized_question = QuestionSerializer(question).data
            answer_options = AnswerOption.objects.filter(question=question)
            serialized_question['answer_options'] = [answer.answer_text for answer in answer_options]
            
            # Find user's answer detail for this question
            user_answer_detail = user_answers.filter(question=question).first()
            if user_answer_detail:
                if user_answer_detail.question.type == "scale":
                    serialized_question['user_answer_text'] = user_answer_detail.answer_point.answer_text
                else:
                    serialized_question['user_answer_text'] = user_answer_detail.answer_text
            
            serialized_questions.append(serialized_question)

        data = {
            "survey": SurveySerializer(survey).data,
            "category": survey.category.name,
            "questions": serialized_questions,
            "tags": TagSerializer(survey.tags.all(), many=True).data
        }
        return Response(data)


## 테스트 1차 테스트 O
class SurveyDelete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        '''
            설문조사 삭제하는 API

            ---
            # Parameters
            - ID : 설문조사 PK
        '''
        survey_to_delete = get_object_or_404(Survey, pk=pk, user=request.user)
        
        if not request.user:
            return Response({"message": "비밀번호가 일치하지 않습니다"}, status=400)
        
        survey_to_delete.delete()
        return Response({"message": "설문 삭제가 완료되었습니다"}, status=200)
    

## 테스트 1차 테스트 O
class SurveyUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        '''
            설문조사 수정내용을 확인하는 API

            ---
            # 내용
                -survey: {
                -    id": 설문조사 PK
                -    title: 설문조사 제목
                -    intro: 설문조사 설명
                -    created_at: 설문조사 작성시간
                -    updated_at: 설문조사 수정시간
                -    enddated_at: 설문조사 종료시간
                -    is_done: 설문조사 활성화상태
                -    views: 설문조사 조회수 
                -    user: 설문조사 작성한 유저
                -    category: 설문조사 카테고리
                -    tags: 설문조사 태그
                -}
                -categories: 카테고리 내용
                -questions: 설문조사 질문 예시답변 내용
                -tags: 태그 내용
        '''
        try:
            survey = Survey.objects.select_related('category', 'user').prefetch_related('question_set__answeroption_set').get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"error": "설문이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

        questions = survey.question_set.all()
        serialized_questions = []

        if request.user:
            user_answers = UserAnswerDetail.objects.filter(useranswer__survey=survey, useranswer__user=request.user)

        for question in questions:
            serialized_question = QuestionSerializer(question).data
            answer_options = AnswerOption.objects.filter(question=question)
            serialized_question['answer_options'] = [answer.answer_text for answer in answer_options]
            serialized_questions.append(serialized_question)

            user_answer_detail = user_answers.filter(question=question).first()
            if user_answer_detail:
                if user_answer_detail.question.type == "scale":
                    serialized_question['user_answer_text'] = user_answer_detail.answer_point.answer_text
                else:
                    serialized_question['user_answer_text'] = user_answer_detail.answer_text

        categories = Category.objects.all()

        data = {
            "survey": SurveySerializer(survey).data,
            "categories": CategorySerializer(categories, many=True).data,
            "questions": serialized_questions,
            "tags": TagSerializer(survey.tags.all(), many=True).data
        }

        return Response(data)
    
    def post(self, request, pk):
        '''
            설문조사를 수정하는 API

            ---
            # Parameters
                -title : 설문조사 제목
                -intro : 설문조사 설명
                -is_done : 설문조사 활성화상태
                -enddated_at : 설문조사 종료시간
                -questions : 설문조사 내용
                -category : 카테고리 내용
                -tags : 태그 내용
        '''
        tags_data = request.data.get('tags')
            
        if tags_data:
            tags = []
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            request.data['tags'] = [tag.id for tag in tags]
            
        survey_instance = get_object_or_404(Survey, pk=pk)

        authentication = JWTAuthentication()
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
        validated_token = authentication.get_validated_token(token)
        
        request.data['user'] = validated_token['user_id']

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
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        '''
            설문조사의 답변 결과를 불러오는 API

            ---
            # Parameters
                -question_qnum : 질문 순서
                -question_text : 질문 내용
                -answer_text : 답변내용
                -count : 답변 갯수
        '''
        try:
            questions = Question.objects.filter(survey_id=pk)
            result = []

            for question in questions:
                answer_options = question.answeroption_set.all()  # 해당 질문에 대한 모든 답변 옵션 가져오기
                question_text = question.question_text

                if question.type == "scale":
                    for answer_option in answer_options:
                        answer_text = answer_option.answer_text
                        answer_count = UserAnswerDetail.objects.filter(
                            useranswer__survey_id=pk,
                            question=question,
                            answer_point=answer_option
                        ).count()
                        result.append({
                            'question_qnum':question.qnum,
                            'question_text': question_text,
                            'answer_text': answer_text,
                            'count': answer_count
                        })
                else:
                    open_text_list = UserAnswerDetail.objects.filter(
                            useranswer__survey_id=pk,
                            question=question
                    )
                    for open_text in open_text_list:
                        result.append({
                            'question_qnum':question.qnum,
                            'question_text': question_text,
                            'answer_text': open_text.answer_text
                        })
            return Response(result, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class UserAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        '''
            설문조사의 답변을 저장하는 API

            ---
            # Parameters
                -survey_id : 설문조사 ID
                -answers : 설문조사 답변내용들
        '''
        # Authenticating the user
        user = request.user
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
            else:
                answer_option = None

            user_answer_detail, detail_created = UserAnswerDetail.objects.get_or_create(
                useranswer=user_answer,
                question=question,
            )
            user_answer_detail.answer_point = answer_option
            user_answer_detail.answer_text = answer_text
            user_answer_detail.save()

        return Response({"message": "설문조사 정보가 저장되었습니다."}, status=status.HTTP_201_CREATED)