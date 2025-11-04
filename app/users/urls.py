from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("create-user/", views.create_user_with_email, name="create_user"),
]
