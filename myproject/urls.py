# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from myapp import views  # 'myapp'はあなたのアプリケーション名に置き換えてください

urlpatterns = [
    path('', views.index_view, name='home'),  # ここで index_view を使用
    path('admin/', admin.site.urls),
    path('accounts/', include('myapp.urls', namespace='myapp')),  # 'myapp' はあなたのアプリケーション名に適切に置き換えてください
]
