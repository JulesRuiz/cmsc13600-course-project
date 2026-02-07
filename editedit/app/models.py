from django.conf import settings
from django.db import models


class UserType(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self) -> str:
        return self.name


class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class ReportingYear(models.Model):
    label = models.CharField(max_length=32, unique=True)

    def __str__(self) -> str:
        return self.label


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="uploads/")

    institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name="uploads")
    reporting_year = models.ForeignKey(ReportingYear, on_delete=models.PROTECT, related_name="uploads")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploads")

    def __str__(self) -> str:
        return f"{self.institution} {self.reporting_year} ({self.uploaded_at:%Y-%m-%d})"


class Fact(models.Model):
    field_key = models.CharField(max_length=255)
    field_value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name="facts")
    reporting_year = models.ForeignKey(ReportingYear, on_delete=models.PROTECT, related_name="facts")
    upload = models.ForeignKey(Upload, on_delete=models.PROTECT, related_name="facts")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="facts_updated")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "reporting_year", "field_key"],
                name="uniq_fact_key_per_institution_year",
            )
        ]

    def __str__(self) -> str:
        return f"{self.institution} {self.reporting_year} {self.field_key}"
