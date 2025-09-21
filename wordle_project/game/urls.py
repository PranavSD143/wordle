from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView,LoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('check_guess/', views.check_guess, name='check_guess'),
    path('admin_home_report/', views.admin_homepage_view, name='admin_home'), 
    path('signup/', views.signup_view, name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('login/', LoginView.as_view(template_name='game/login.html'), name='login'),
    path('api/state/', views.get_game_state_api, name='api_game_state'),
]