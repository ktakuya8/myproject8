from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import CustomUserCreationForm, FoodRecordForm, ExerciseRecordForm, SleepRecordForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser, FoodRecord, ExerciseRecord, SleepRecord, UserProfile
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Sum
from datetime import datetime

def calculate_age(birthdate):
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def get_recommended_calories(age, gender):
    calories_by_age_gender = {
        '男性': {'1-2': 950, '3-5': 1300, '6-7': 1550, '8-9': 1850, '10-11': 2250, '12-14': 2600, '15-17': 2800, '18-29': 2650, '30-49': 2700, '50-64': 2600, '65-74': 2400, '75+': 2100},
        '女性': {'1-2': 900, '3-5': 1250, '6-7': 1450, '8-9': 1700, '10-11': 2100, '12-14': 2400, '15-17': 2300, '18-29': 2000, '30-49': 2050, '50-64': 1950, '65-74': 1850, '75+': 1650}
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


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user, backend='myapp.authentication.EmailBackend')  
            print(request.user.is_authenticated)  
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
            print(request.user.is_authenticated) 
            return redirect('myapp:main_menu')
        else:
            print("Invalid login attempt") 
            return render(request, 'registration/login.html', {'error': 'Invalid email or password'})
    else:
        return render(request, 'registration/login.html')


def my_logout_view(request):
    logout(request)
    return redirect('myapp:login')

def calculate_age(birthdate):
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def get_recommended_calories(age, gender):
    calories_by_age_gender = {
        '男性': {'1-2': 950, '3-5': 1300, '6-7': 1550, '8-9': 1850, '10-11': 2250, '12-14': 2600, '15-17': 2800, '18-29': 2650, '30-49': 2700, '50-64': 2600, '65-74': 2400, '75+': 2100},
        '女性': {'1-2': 900, '3-5': 1250, '6-7': 1450, '8-9': 1700, '10-11': 2100, '12-14': 2400, '15-17': 2300, '18-29': 2000, '30-49': 2050, '50-64': 1950, '65-74': 1850, '75+': 1650}
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

from django.utils import timezone
from django.db.models import Sum

@login_required
def main_menu(request):
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    user_profile = UserProfile.objects.get(user=request.user)
    target_calories = user_profile.target_calories
    target_exercise_minutes = user_profile.target_exercise_minutes
    target_sleep_hours = user_profile.target_sleep_hours

    # 昨日の記録を取得
    yesterday_food = FoodRecord.objects.filter(user=request.user, date=yesterday).aggregate(Sum('calories'))
    yesterday_exercise = ExerciseRecord.objects.filter(user=request.user, date=yesterday).aggregate(Sum('duration'))
    yesterday_sleep = SleepRecord.objects.filter(user=request.user, date=yesterday).aggregate(Sum('duration'))

    # 達成度をパーセンテージで計算
    food_achievement = (yesterday_food['calories__sum'] / target_calories * 100) if yesterday_food['calories__sum'] else 0
    exercise_achievement = (yesterday_exercise['duration__sum'] / target_exercise_minutes * 100) if yesterday_exercise['duration__sum'] else 0
    sleep_achievement = (yesterday_sleep['duration__sum'] / target_sleep_hours * 100) if yesterday_sleep['duration__sum'] else 0

    context = {
        'recommended_calories': get_recommended_calories(calculate_age(request.user.birth_date), request.user.gender),
        'target_calories': target_calories,
        'target_exercise_minutes': target_exercise_minutes,
        'target_sleep_hours': target_sleep_hours,
        'food_achievement': round(food_achievement, 2),
        'exercise_achievement': round(exercise_achievement, 2),
        'sleep_achievement': round(sleep_achievement, 2),
        'past_week_food': [record.calories for record in FoodRecord.objects.filter(user=request.user).order_by('-date')[:7]],
        'past_week_exercise': [record.duration for record in ExerciseRecord.objects.filter(user=request.user).order_by('-date')[:7]],
        'past_week_sleep': [record.duration for record in SleepRecord.objects.filter(user=request.user).order_by('-date')[:7]],
    }
    return render(request, 'main_menu.html', context)



    past_week_data = {
        'food': [record.calories for record in FoodRecord.objects.filter(user=request.user).order_by('-date')[:7]],
        'exercise': [record.duration for record in ExerciseRecord.objects.filter(user=request.user).order_by('-date')[:7]],
        'sleep': [record.duration for record in SleepRecord.objects.filter(user=request.user).order_by('-date')[:7]]
    }
   
    future_prediction = {
        'food': sum(past_week_data['food']) / len(past_week_data['food']) if past_week_data['food'] else 0,
        'exercise': sum(past_week_data['exercise']) / len(past_week_data['exercise']) if past_week_data['exercise'] else 0,
        'sleep': sum(past_week_data['sleep']) / len(past_week_data['sleep']) if past_week_data['sleep'] else 0
    }

    context = {
        'recommended_calories': recommended_calories,
        'past_week_food': past_week_data['food'],
        'past_week_exercise': past_week_data['exercise'],
        'past_week_sleep': past_week_data['sleep'],
        'future_prediction_food': future_prediction['food'],
        'future_prediction_exercise': future_prediction['exercise'],
        'future_prediction_sleep': future_prediction['sleep']
    }
    return render(request, 'main_menu.html', context)



@login_required
def food_record(request):
    user_profile = UserProfile.objects.get(user=request.user)
    birthdate = user_profile.user.birth_date
    gender = 'M' if user_profile.user.gender == '男' else 'F'  
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    recommended_calories = get_recommended_calories(age, gender)
    recommended_calories_plus_500 = recommended_calories + 500
    recommended_calories_minus_500 = recommended_calories - 500

   
    calories_by_age_gender = get_calories_by_age_gender()

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
        'calories_by_age_gender': calories_by_age_gender,  
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
        'F':{'1-2': 900, '3-5': 1250, '6-7': 1450, '8-9': 1700, '10-11': 2100, '12-14': 2400, '15-17': 2300, '18-29': 2000, '30-49': 2050, '50-64': 1950, '65-74': 1850, '75+': 1650}
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
    today = date.today()
    five_days_ago = today - timedelta(days=5)

    if request.method == 'POST':
        form = ExerciseRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.date = today  
            record.save()
            return redirect('myapp:exercise_record')  
    else:
        form = ExerciseRecordForm()

    exercise_records = ExerciseRecord.objects.filter(
        user=request.user,
        date__gte=five_days_ago
    ).order_by('-date')

    return render(request, 'exercise_record.html', {
        'form': form,
        'exercise_records': exercise_records
    })

@login_required
def sleep_record(request):
    today = date.today()
    five_days_ago = today - timedelta(days=5)
    
    if request.method == 'POST':
        form = SleepRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.date = today  
            return redirect('myapp:sleep_record')  
    else:
        form = SleepRecordForm()

    sleep_records = SleepRecord.objects.filter(
        user=request.user,
        date__gte=five_days_ago
    ).order_by('-date')

    return render(request, 'sleep_record.html', {
        'form': form,
        'sleep_records': sleep_records
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

def get_calories_by_age_gender():
    return {
        '男性': {
            '1-2': 950, '3-5': 1300, '6-7': 1550, '8-9': 1850, '10-11': 2250,
            '12-14': 2600, '15-17': 2800, '18-29': 2650, '30-49': 2700,
            '50-64': 2600, '65-74': 2400, '75+': 2100
        },
        '女性': {
            '1-2': 900, '3-5': 1250, '6-7': 1450, '8-9': 1700, '10-11': 2100,
            '12-14': 2400, '15-17': 2300, '18-29': 2000, '30-49': 2050,
            '50-64': 1950, '65-74': 1850, '75+': 1650
        }
    }

