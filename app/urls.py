from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_user_form, name="new_user_form"),
    path("api/createUser/", views.create_user_api, name="create_user_api"),
]
