from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    
    GENDER_CHOICES = [
        ('M', _('男性')),
        ('F', _('女性')),
     ]

    
    email = models.EmailField(_('email address'), unique=True) 
    birth_date = models.DateField(_('生年月日'), null=True, blank=True)
    gender = models.CharField(_('性別'), max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

class FoodRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('ユーザー'))
    date = models.DateField(_('日付'))
    calories = models.IntegerField(_('カロリー'))
    description = models.TextField(_('説明'), blank=True, null=True)

    def save(self, *args, **kwargs):
        
        existing_record = FoodRecord.objects.filter(user=self.user, date=self.date).first()
        if existing_record:
         
            existing_record.calories = self.calories
            existing_record.description = self.description
            super(FoodRecord, existing_record).save(*args, **kwargs)
        else:
            
            super(FoodRecord, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'date')  

class ExerciseRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('ユーザー'))
    date = models.DateField(_('日付'))
    duration = models.IntegerField(_('運動時間（分）'))
    activity_type = models.CharField(_('活動タイプ'), max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
       
        existing_record = ExerciseRecord.objects.filter(user=self.user, date=self.date).first()
        if existing_record:
          
            existing_record.duration = self.duration
            existing_record.activity_type = self.activity_type
            super(ExerciseRecord, existing_record).save(*args, **kwargs)
        else:
            
            super(ExerciseRecord, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'date')  


class SleepRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('ユーザー'))
    date = models.DateField(_('日付'))
    duration = models.IntegerField(_('睡眠時間（分）'))
    quality = models.CharField(_('睡眠の質'), max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        existing_record = SleepRecord.objects.filter(user=self.user, date=self.date).first()
        if existing_record:
            existing_record.duration = self.duration
            existing_record.quality = self.quality
            super(SleepRecord, existing_record).save(*args, **kwargs)
        else:
            super(SleepRecord, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'date') 


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name=_('ユーザー'))
    target_calories = models.IntegerField(_('目標カロリー'), default=2000)
    target_exercise_minutes = models.IntegerField(_('目標運動時間（分）'), default=60)
    target_sleep_hours = models.IntegerField(_('目標睡眠時間（時間）'), default=8)
