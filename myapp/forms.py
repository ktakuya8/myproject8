from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, FoodRecord, ExerciseRecord, SleepRecord

class CustomUserCreationForm(UserCreationForm):
    birth_date = forms.DateField(label='生年月日', widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(label='性別', choices=CustomUser.GENDER_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'birth_date', 'gender']
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'password1': 'パスワード',
            'password2': 'パスワード（確認）'
        }

class FoodRecordForm(forms.ModelForm):
    class Meta:
        model = FoodRecord
        fields = ['date', 'calories', 'description']
        labels = {
            'date': '日付',
            'calories': 'カロリー',
            'description': '内容'
        }

class ExerciseRecordForm(forms.ModelForm):
    class Meta:
        model = ExerciseRecord
        fields = ['date', 'duration', 'activity_type']
        labels = {
            'date': '日付',
            'duration': '時間',
            'activity_type': '活動種類'
        }

class SleepRecordForm(forms.ModelForm):
    class Meta:
        model = SleepRecord
        fields = ['date', 'duration', 'quality']
        labels = {
            'date': '日付',
            'duration': '時間',
            'quality': '睡眠の質'
        }
