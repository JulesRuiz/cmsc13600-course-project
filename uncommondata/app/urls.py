from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('editpage', views.editpage, name='editpage'),
    path('api/createUser/', views.createUser, name='createUser'),
    path('api/upload/', views.uploads, name='upload'),
    path('api/dump-uploads/', views.dump_uploads, name='dump_uploads'),
    path('api/dump-data/', views.dump_data, name='dump_data'),
    path('api/knockknock/', views.knockknock, name='knockknock'),
    path('uploads/', views.upload, name='uploads'),
    path('api/download/<int:id>/', views.download, name='download'),
    path('api/process/<int:id>/', views.process, name='process'),
]
