from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

import os
import requests

from .models import Upload, Institution, ReportingYear

''' Views to process POST requests to update 
wikipedia-like content in databse '''

def index(request):
    return HttpResponse("OK")

@csrf_exempt
def editpage(request):
    return HttpResponse("")

def _is_curator(user) -> bool:
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@require_POST
def createUser(request):
    """
    Test harness endpoint: creates a user.
    Expected POST fields:
      user_name, password, email (optional), is_curator (0/1)
    """
    User = get_user_model()

    username = (request.POST.get("user_name") or "").strip()
    password = request.POST.get("password") or ""
    email = (request.POST.get("email") or "").strip()
    is_curator = (request.POST.get("is_curator") or "0").strip()

    if not username or not password:
        return JsonResponse({"error": "Missing user_name or password"}, status=400)

    user, created = User.objects.get_or_create(username=username, defaults={"email": email})
    if email and user.email != email:
        user.email = email

    user.set_password(password)

    if is_curator == "1":
        user.is_staff = True

    user.save()

    inst, _ = Institution.objects.get_or_create(name="Autograder University")
    ry, _ = ReportingYear.objects.get_or_create(label="2024-2025")

    if not Upload.objects.filter(uploaded_by=user).exists():
        up = Upload.objects.create(
             institution=inst,
             reporting_year=ry,
             uploaded_by=user,
             url=None,
        )
        up.file.save("seed.txt", ContentFile(b"seed"), save=True)
    return JsonResponse({"created": created, "username": user.username}, status=201 if created else 200)

@require_GET
def uploads(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    if _is_curator(request.user):
        return HttpResponse(status=403)

    qs = (
        Upload.objects
        .filter(uploaded_by=request.user)
        .select_related("institution", "reporting_year")
        .order_by("-uploaded_at")
    )

    return render(request, "uploads.html", {"uploads": qs})

@require_POST
def upload(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    institution_name = (request.POST.get("institution") or "").strip()
    year_label = (request.POST.get("year") or "").strip()
    url = (request.POST.get("url") or "").strip() or None
    file_obj = request.FILES.get("file") or request.FILES.get("upload")

    if not institution_name or not year_label or file_obj is None:
        return JsonResponse({"error": "Missing field(s)."}, status=400)

    institution, _ = Institution.objects.get_or_create(name=institution_name)
    reporting_year, _ = ReportingYear.objects.get_or_create(label=year_label)

    up = Upload.objects.create(
        institution=institution,
        reporting_year=reporting_year,
        uploaded_by=request.user,
        file=file_obj,
    )

    if hasattr(up, "url"):
        up.url = url
        up.save(update_fields=["url"])

    return JsonResponse({"id": str(up.id)}, status=201)


@require_GET
def dump_uploads(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    if request.user.is_staff or request.user.is_superuser:
        qs = Upload.objects.select_related("institution", "reporting_year", "uploaded_by").all()
    else:
        qs = Upload.objects.select_related("institution", "reporting_year", "uploaded_by").filter(
            uploaded_by=request.user
        )

    data = {}
    for up in qs.order_by("id"):
        data[str(up.id)] = {
            "user": up.uploaded_by.username,
            "institution": up.institution.name,
            "year": up.reporting_year.label,
            "url": up.url if getattr(up, "url", None) else None,
            "file": up.file.name.split("/")[-1] if up.file else None,
        }

    return JsonResponse(data, status=200)

@require_GET
def dump_data(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if not _is_curator(request.user):
        return HttpResponse(status=403)
    return HttpResponse("OK", status=200)


@require_GET
def knockknock(request):
    topic = (request.GET.get("topic") or "banana").strip()[:40]
    canned = f"Knock knock.\nWho's there?\n{topic}.\n{topic} who?\n{topic} you glad I didn't say banana?"
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return HttpResponse(canned, content_type="text/plain", status=200)

    prompt = f'Write a short knock-knock joke about "{topic}". Max 6 lines.'

    try:
        resp = requests.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4.1-mini", "input": prompt},
            timeout=30,
        )
        if resp.status_code != 200:
            return HttpResponse(canned, content_type="text/plain", status=200)

        data = resp.json()
        text = None
        out = data.get("output")
        if isinstance(out, list) and out:
            content = out[0].get("content")
            if isinstance(content, list) and content:
                text = content[0].get("text")

        return HttpResponse((text or canned).strip(), content_type="text/plain", status=200)
    except Exception:
        return HttpResponse(canned, content_type="text/plain", status=200)
