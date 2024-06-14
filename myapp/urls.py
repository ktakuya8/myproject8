from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'), 
    path('login/', views.my_login_view, name='login'),
    path('signup/', views.register, name='signup'),
    path('logout/', views.my_logout_view, name='logout'),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('food_record/', views.food_record, name='food_record'),
    path('food_record/submit/', views.submit_food_record, name='submit_food_record'),
    path('sleep_record/', views.sleep_record, name='sleep_record'),
    path('exercise_record/', views.exercise_record, name='exercise_record'),
    path('exercise_record/submit/', views.submit_exercise_record, name='submit_exercise_record'),
    path('sleep_record/submit/', views.submit_sleep_record, name='submit_sleep_record')
]
