# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('myapp.urls', namespace='myapp')),  # 'myapp'のURLを'accounts/'プレフィックスで包含
]
