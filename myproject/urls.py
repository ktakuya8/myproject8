from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/'), name='go-to-login'),  # ルートからログインページへリダイレクト
    path('admin/', admin.site.urls),
    path('accounts/', include('myapp.urls', namespace='myapp')),
]
