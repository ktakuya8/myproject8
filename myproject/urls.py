
from django.contrib import admin
from django.urls import path, include
from myapp import views  

urlpatterns = [
    path('', views.index_view, name='home'),  
    path('admin/', admin.site.urls),
    path('accounts/', include('myapp.urls', namespace='myapp')),  
]
