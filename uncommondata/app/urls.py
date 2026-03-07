from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("editpage", views.editpage, name="editpage"),

    path("api/upload/", views.upload, name="upload"),
    path("api/dump-uploads/", views.dump_uploads, name="dump_uploads"),
    path("api/download/<str:id>/", views.download, name="download"),
    path("api/process/<str:id>/", views.process, name="process"),
    path("api/knockknock/", views.knockknock, name="knockknock"),

    path("show-uploads/", views.show_uploads, name="show_uploads"),
]
