from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_home),
    path('register', views.user_register),
    path('login', views.user_login),
    path('logout', views.user_logout),
    path('refresh-token', views.refresh_token_view),
    path('delete', views.user_delete),
    path('update', views.user_update),
    path('update/password', views.user_update_password),
    path('forget/password', views.user_forget_password),
]
