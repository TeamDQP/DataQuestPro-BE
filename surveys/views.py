from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Survey, Category, Tag, Question, Answer
from .serializers import SurveySerializer, CategorySerializer, TagSerializer, QuestionSerializer, AnswerSerializer

# Create your views here.
### Survey
class Survey_Create(APIView):

    def post(self, request):
        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)  # 현재 로그인한 사용자를 Survey의 user 필드에 연결
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    
### category
class Category_Create(APIView):

    def post(slef, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

### Tag
class Tag_Create(APIView):

    def post(slef, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)