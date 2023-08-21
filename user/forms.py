from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            'required': '이메일 형식을 입력해주세요'
        },
        max_length=50, label='Email', required=True, help_text='유효한 이메일 주소를 입력하세요'
    )


    password = forms.CharField(
        error_messages={
            'required': '비밀번호를 입력해 주세요.',
        },
        max_length=18, min_length=6, widget=forms.PasswordInput, label='비밀번호'
    )




    re_password = forms.CharField(
        error_messages={
            'required': '비밀번호를 다시 입력해주세요'
        },
        widget=forms.PasswordInput, label='비밀번호', max_length=18, min_length=6,
        help_text='유효한 비밀번호를 입력하세요'
    )