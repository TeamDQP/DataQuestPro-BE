from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ProfileSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import Profile
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterView(APIView):

    def post(self, request):
        '''
            회원가입을 위한 데이터를 저장하는 API

        ---
        # 내용
            - email : 가입할 회원의 email, username 대신 email을 사용
            - password : 가입할 회원의 비밀번호
            - name : 가입할 회원의 이름
            - email_opt_in : 이메일 수신 동의 여부 확인
        '''
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    '''
        로그인을 위한 API

    ---
    # 내용
        - email : 로그인 하는 회원의 email
        - password : 해당 email에 대한 회원의 비밀번호
    '''
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    '''
        access token 재발급을 위한 API

    ---
    # 내용
        - refresh : 로그인 시 발급된 refresh token
    '''


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        '''
        로그아웃을 위한 API

        ---
        # 내용
            - refresh : 로그인 시 발급된 refresh token
        '''
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class JWTValidationView(APIView):
    # The user is authenticated,
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        access toekn의 유효성을 검증하기 위한 API

        ---
        # 내용
            - 로그인 시 발급된 accss token. header에 포함시켜 요청
        '''
        try:
            # # the token is valid
            token = AccessToken(request.META.get(
                'HTTP_AUTHORIZATION').split(' ')[-1])
            return Response('Token Validated', status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class EmailVerification(APIView):
    def get(self, request, pk):
        '''
        회원 가입시 등록한 email의 실제 사용 여부를 인증하여 active user로 전환하기 위한 API

        ---
        # 내용
            - id : 회원가입시 등록한 이메일로 전송되는 회원가입 이메일 안의 인증 링크에 포함된 user의 pk값
        '''
        try:
            user = User.objects.get(pk=pk)
            if user.is_sleeping:
                user.is_sleeping = False
                user.save()
                return Response('wake', status=status.HTTP_200_OK)
            return Response('Email has already been verified.', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        '''
        회원정보를 수정하기 위해 저장된 데이터를 불러오는 API

        ---
        # 내용
            - email : 회원의 현재 email
            - password : 회원의 현재 비밀번호
            - name : 회원의 현재 이름
            - email_opt_in : 현재 회원의 이메일 수신 동의 여부 값
        '''
        user = User.objects.get(email=request.user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        '''
        회원정보를 수정하기 위해 수정된 데이터를 저장하는 API

        ---
        # 내용
            - email : 회원의 수정할 email
            - password : 회원의 수정할 비밀번호
            - name : 회원의 수정할 이름
            - email_opt_in : 수정된 회원의 이메일 수신 동의 여부 값
        '''
        user = User.objects.get(email=request.user)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        '''
        회원탈퇴를 위한 API

        ---
        # 내용
            - request.user : 회원을 탈퇴할 유저의 email. 
            - 탈퇴시 inactive 상태로 변경후 DB에 유저 데이터는 보관.
        '''
        user = User.objects.get(email=request.user)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_404_NOT_FOUND)


class ProfileWrite(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        '''
        회원 프로필을 생성하기 위한 API

        ---
        # 내용
            - profileimage: 유저가 사용할 프로필 이미지
            - username: 유저가 사용할 별명
            - 회원가입 시 자동으로 기본 프로필 생성됨.
        '''
        # user = request.data.get('user')
        # image = request.data.get('image')
        # username = request.data.get('username')
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileRead(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        '''
        회원 프로필을 불러오기 위한 API

        ---
        # 내용
            - profileimage: 유저의 프로필 이미지
            - username: 유저의 별명
        '''
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        '''
        회원 프로필을 수정하기 위한 API

        ---
        # 내용
            - profileimage: 현재 유저의 프로필 이미지
            - username: 현재 유저의 별명
        '''
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request):
        '''
        회원 프로필을 수정하기 위한 API

        ---
        # 내용
            - profileimage: 수정할 유저의 프로필 이미지
            - username: 수정할 유저의 별명
        '''
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            # print(request.data)
            # print(serializer.validated_data['profileimage'])
            # print(type(serializer.validated_data['profileimage']))
            if serializer.validated_data['profileimage']:
                serializer.save()
            else:
                # print('null')
                serializer.save(profileimage=profile.profileimage)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):  # request 안에 user가 있으므로 pk가 필요없음.
        '''
        회원 프로필을 삭제하기 위한 API

        ---
        # 내용
            - request.user :  프로필 삭제할 유저의 email
        '''
        profile = Profile.objects.get(user=request.user)
        profile.delete()
        return Response(status=status.HTTP_404_NOT_FOUND)
