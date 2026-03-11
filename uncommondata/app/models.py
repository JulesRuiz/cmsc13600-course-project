from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

import hashlib

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Page(models.Model):
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PageRevision(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='revisions')
    content = models.TextField()
    editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page.title} - Revision {self.id}"


class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ReportingYear(models.Model):
    label = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.label


class Upload(models.Model):
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    reporting_year = models.ForeignKey(ReportingYear, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/")
    url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploaded_by.username} - {self.file.name}"

    @staticmethod
    def sha256_for_file(file_obj) -> str:
        hasher = hashlib.sha256()
        for chunk in file_obj.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()