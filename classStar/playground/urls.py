from django.conf import urls
from django.urls import path
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
	path('signup/', views.signup, name='signup'),
	path('accounts/login/', LoginView.as_view(template_name='playground/login.html'), name='login'),
	path('accounts/logout/', LogoutView.as_view(template_name='playground/login.html'), name='logout'),
    path('', views.index, name='index'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('users/', views.users, name='users'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<str:course_code>/', views.posts_under_course, name='posts_under_course'),
    path('makepost/', views.makePost, name="makepost"),
    path('post/<int:post_id>/', views.post_details, name='post_details'),
    path('vote/<int:post_id>/<str:status>/', views.vote, name='vote'),
]
