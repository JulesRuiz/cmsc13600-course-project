from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("editpage", views.editpage, name="editpage"),

    path("api/createUser/", views.create_user, name="create_user"),
    path("api/upload/", views.upload, name="upload"),
    path("api/dump-uploads/", views.dump_uploads, name="dump_uploads"),
    path("api/dump-data/", views.dump_data, name="dump_data"),
    path("api/download/<str:id>/", views.download, name="download"),
    path("api/process/<str:id>/", views.process, name="process"),
    path("api/knockknock/", views.knockknock, name="knockknock"),
    path("uploads/", views.uploads_page, name="uploads_page"),
    path("show-uploads/", views.show_uploads, name="show_uploads"),
]
