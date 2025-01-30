from django.urls import path
from .views import Sign_up, Login  # Sign_up 뷰를 import

urlpatterns = [
    path('/sign-up', Sign_up.as_view(), name='sign-up'),
    # 다른 URL 패턴들...
    path('/login', Login.as_view(), name='login'),
]
