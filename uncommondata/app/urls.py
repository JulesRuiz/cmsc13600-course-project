from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path("", views.index, name="index"),
    path("new/", views.new_user_form, name="new_user_form"),
    path("api/createUser/", views.create_user_api, name="create_user_api"),
=======
    path('', views.index, name='index'),
    path('editpage', views.editpage, name='editpage'),
    path("api/createUser/", views.createUser, name="createUser"),
    path('api/upload/', views.upload, name='upload'),
    path('api/dump-uploads/', views.dump_uploads, name='dump_uploads'),
    path('api/dump-data/', views.dump_data, name='dump_data'),
    path('api/knockknock/', views.knockknock, name='knockknock'),
    path('uploads/', views.uploads, name='uploads'),
>>>>>>> 720d40a (Fixed files for HW5 submission)
]
