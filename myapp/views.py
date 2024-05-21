from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import CustomUserCreationForm, FoodRecordForm, ExerciseRecordForm, SleepRecordForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser, FoodRecord, ExerciseRecord, SleepRecord, UserProfile
from django.utils import timezone
from datetime import date, timedelta

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user, backend='myapp.authentication.EmailBackend')  # backend 属性を設定
            print(request.user.is_authenticated)  # 登録とログイン後の認証状態を確認
            return redirect('myapp:main_menu')
        else:
            print("Form errors", form.errors)
            print("Submitted birth date:", request.POST.get('birth_date'))
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def my_login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            print(request.user.is_authenticated)  # ログイン後の認証状態を確認
            return redirect('myapp:main_menu')
        else:
            print("Invalid login attempt")  # 認証失敗を確認
            return render(request, 'registration/login.html', {'error': 'Invalid email or password'})
    else:
        return render(request, 'registration/login.html')


def my_logout_view(request):
    logout(request)
    return redirect('myapp:login')

@login_required
def main_menu(request):
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'target_calories': 2000,
            'target_exercise_minutes': 60,
            'target_sleep_hours': 8
        }
    )
    yesterday = timezone.now().date() - timedelta(days=1)
    records = {
        'food': FoodRecord.objects.filter(user=request.user, date=yesterday).first(),
        'exercise': ExerciseRecord.objects.filter(user=request.user, date=yesterday).first(),
        'sleep': SleepRecord.objects.filter(user=request.user, date=yesterday).first()
    }
    achievements = {}
    achieved_attrs = {
        'food': 'calories',
        'exercise': 'duration',
        'sleep': 'duration'
    }
    for key, record in records.items():
        if record:
            target_attr = f'target_{key}_calories' if key == 'food' else f'target_{key}_minutes' if key == 'exercise' else f'target_{key}_hours'
            target = getattr(user_profile, target_attr, 0)
            achieved = getattr(record, achieved_attrs[key], 0)
            achievements[f'{key}_achievement'] = (achieved / target * 100) if target else 0
        else:
            achievements[f'{key}_achievement'] = "No data"

    past_week_data = {
        'food': [record.calories for record in FoodRecord.objects.filter(user=request.user).order_by('-date')[:7]],
        'exercise': [record.duration for record in ExerciseRecord.objects.filter(user=request.user).order_by('-date')[:7]],
        'sleep': [record.duration for record in SleepRecord.objects.filter(user=request.user).order_by('-date')[:7]]
    }

    context = {
        **achievements,
        'past_week_food': past_week_data['food'],
        'past_week_exercise': past_week_data['exercise'],
        'past_week_sleep': past_week_data['sleep']
    }
    return render(request, 'main_menu.html', context)

@login_required
def food_record(request):
    user_profile = UserProfile.objects.get(user=request.user)
    birthdate = user_profile.user.birth_date
    gender = 'M' if user_profile.user.gender == '男' else 'F'  # 性別を変換
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    recommended_calories = get_recommended_calories(age, gender)
    recommended_calories_plus_500 = recommended_calories + 500
    recommended_calories_minus_500 = recommended_calories - 500

    form = FoodRecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.user = request.user
        record.date = form.cleaned_data['date']
        record.save()
        return redirect('myapp:food_record')

    food_records = FoodRecord.objects.filter(user=request.user).order_by('-date')
    yesterday_calories = food_records.first().calories if food_records.exists() else 0
    goal_calories = user_profile.target_calories
    achievement_percent = (yesterday_calories / goal_calories * 100) if goal_calories else 0

    past_five_days_records = FoodRecord.objects.filter(user=request.user).order_by('-date')[:5]

    context = {
        'form': form,
        'recommended_calories': recommended_calories,
        'recommended_calories_plus_500': recommended_calories_plus_500,
        'recommended_calories_minus_500': recommended_calories_minus_500,
        'food_records': food_records,
        'birthdate': birthdate,
        'gender': gender,
        'age': age,
        'today': today,
        'yesterday_calories': yesterday_calories,
        'goal_calories': goal_calories,
        'achievement_percent': achievement_percent,
        'past_five_days_records': past_five_days_records,
    }
    return render(request, 'food_record.html', context)

def get_recommended_calories(age, gender):
    calories_by_age_gender = {
        'M': {'1-2': 950, '3-5': 1300, '6-7': 1550, '8-9': 1850, '10-11': 2250, '12-14': 2600, '15-17': 2800, '18-29': 2650, '30-49': 2700, '50-64': 2600, '65-74': 2400, '75+': 2100},
        'F': {'1-2': 900, '3-5': 1250, '6-7': 1450, '8-9': 1700, '10-11': 2100, '12-14': 2400, '15-17': 2300, '18-29': 2000, '30-49': 2050, '50-64': 1950, '65-74': 1850, '75+': 1650}
    }
    for age_range, calories in calories_by_age_gender[gender].items():
        if '+' in age_range:
            min_age = int(age_range.split('+')[0])
            if age >= min_age:
                return calories
        else:
            min_age, max_age = map(int, age_range.split('-'))
            if min_age <= age <= max_age:
                return calories
    return 0

@login_required
def exercise_record(request):
    if request.method == 'POST':
        form = ExerciseRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('myapp:exercise_record')
    else:
        form = ExerciseRecordForm()
    return render(request, 'exercise_record.html', {
        'form': form,
        'exercise_records': ExerciseRecord.objects.filter(user=request.user).order_by('-date')
    })

@login_required
def sleep_record(request):
    if request.method == 'POST':
        form = SleepRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('myapp:sleep_record')
    else:
        form = SleepRecordForm()
    return render(request, 'sleep_record.html', {
        'form': form,
        'sleep_records': SleepRecord.objects.filter(user=request.user).order_by('-date')
    })

@login_required
def submit_food_record(request):
    if request.method == 'POST':
        form = FoodRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('myapp:food_record')
    return redirect('myapp:food_record')

@login_required
def submit_exercise_record(request):
    if request.method == 'POST':
        form = ExerciseRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('myapp:exercise_record')
    return redirect('myapp:exercise_record')

@login_required
def submit_sleep_record(request):
    if request.method == 'POST':
        form = SleepRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('myapp:sleep_record')
    return redirect('myapp:sleep_record')

def index(request):
    return HttpResponse("Hello, world. This is the index page.")
