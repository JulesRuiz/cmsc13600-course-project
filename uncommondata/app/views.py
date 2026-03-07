from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import get_user_model

from .models import Upload, Institution, ReportingYear


def index(request):
    return HttpResponse("OK")


@csrf_exempt
def editpage(request):
    return HttpResponse("")


def _is_curator(user) -> bool:
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@require_POST
def createUser(request):
    User = get_user_model()

    username = (request.POST.get("user_name") or "").strip()
    password = request.POST.get("password") or ""
    email = (request.POST.get("email") or "").strip()
    is_curator = (request.POST.get("is_curator") or "0").strip()

    if not username or not password:
        return JsonResponse({"error": "Missing user_name or password"}, status=400)

    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email},
    )

    if email and user.email != email:
        user.email = email

    user.set_password(password)

    if is_curator == "1":
        user.is_staff = True

    user.save()

    return JsonResponse(
        {"created": created, "username": user.username},
        status=201 if created else 200,
    )


@require_GET
def uploads(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")

    if _is_curator(request.user):
        qs = Upload.objects.select_related(
            "institution", "reporting_year", "uploaded_by"
        ).order_by("-uploaded_at")
    else:
        qs = (
            Upload.objects
            .filter(uploaded_by=request.user)
            .select_related("institution", "reporting_year", "uploaded_by")
            .order_by("-uploaded_at")
        )

    return render(request, "uploads.html", {"uploads": qs})

@require_GET
def dump_uploads(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    if _is_curator(request.user):
        qs = Upload.objects.select_related(
            "institution", "reporting_year", "uploaded_by"
        ).all()
    else:
        qs = Upload.objects.select_related(
            "institution", "reporting_year", "uploaded_by"
        ).filter(uploaded_by=request.user)

    data = {}
    for up in qs.order_by("id"):
        data[str(up.id)] = {
            "user": up.uploaded_by.username,
            "institution": up.institution.name,
            "year": up.reporting_year.label,
            "url": up.url,
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
    joke = (
        f"Knock knock.\n"
        f"Who's there?\n"
        f"{topic}.\n"
        f"{topic} who?\n"
        f"{topic} you glad I didn't say banana?"
    )
    return HttpResponse(joke, content_type="text/plain", status=200)


@require_GET
def download(request, id):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    up = get_object_or_404(Upload, id=id)

    if not _is_curator(request.user) and up.uploaded_by != request.user:
        return HttpResponse(status=403)

    return FileResponse(up.file.open("rb"), as_attachment=True)


@require_GET
def process(request, id):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    up = get_object_or_404(Upload, id=id)

    if not _is_curator(request.user) and up.uploaded_by != request.user:
        return HttpResponse(status=403)

    data = {
        "tuition_undergraduates": None,
        "required_fees_undergraduates": None,
        "food_and_housing_on_campus_undergraduates": None,
        "housing_only_on_campus_undergraduates": None,
        "food_only_on_campus_meal_plan_undergraduates": None,
        "degree_seeking_undergraduate_students": None,
        "applied_for_need_based_financial_aid": None,
        "determined_to_have_financial_need": None,
        "awarded_any_financial_aid": None,
        "average_financial_aid_package": None,
        "men_applied": None,
        "women_applied": None,
        "another_gender_applied": None,
        "unknown_gender_applied": None,
        "men_admitted": None,
        "women_admitted": None,
        "another_gender_admitted": None,
        "unknown_gender_admitted": None,
    }

    return JsonResponse(data, status=200)

