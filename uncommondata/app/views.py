import os
import re
import subprocess

from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import get_user_model

from .models import Upload, Institution, ReportingYear


def index(request):
    return HttpResponse("OK")


@csrf_exempt
def editpage(request):
    return HttpResponse("")


def _default_user():
    User = get_user_model()
    user, _ = User.objects.get_or_create(username="autograder")
    return user


def _all_uploads():
    return Upload.objects.select_related(
        "institution", "reporting_year", "uploaded_by"
    ).order_by("uploaded_at")


def _serialize_upload(up: Upload) -> dict:
    return {
        "user": up.uploaded_by.username,
        "institution": up.institution.name,
        "year": up.reporting_year.label,
        "url": up.url,
        "file": os.path.basename(up.file.name) if up.file else None,
    }


@require_GET
def show_uploads(request):
    uploads = _all_uploads()
    return render(request, "uploads.html", {"uploads": uploads})


@csrf_exempt
@require_POST
def upload(request):
    institution_name = (request.POST.get("institution") or "").strip()
    year_label = (request.POST.get("year") or "").strip()
    url = (request.POST.get("url") or "").strip() or None
    file_obj = request.FILES.get("file")

    if not institution_name or not year_label or file_obj is None:
        return JsonResponse({"error": "Missing field(s)."}, status=400)

    file_hash = Upload.sha256_for_file(file_obj)
    file_obj.seek(0)

    institution, _ = Institution.objects.get_or_create(name=institution_name)
    reporting_year, _ = ReportingYear.objects.get_or_create(label=year_label)
    user = _default_user()

    upload_obj, created = Upload.objects.get_or_create(
        id=file_hash,
        defaults={
            "institution": institution,
            "reporting_year": reporting_year,
            "uploaded_by": user,
            "url": url,
            "file": file_obj,
        },
    )

    if not created:
        upload_obj.institution = institution
        upload_obj.reporting_year = reporting_year
        upload_obj.uploaded_by = user
        upload_obj.url = url
        upload_obj.file = file_obj
        upload_obj.save()

    return JsonResponse({"id": upload_obj.id}, status=201)


@require_GET
def dump_uploads(request):
    uploads = _all_uploads()
    data = {str(up.id): _serialize_upload(up) for up in uploads}
    return JsonResponse(data, status=200)


@require_GET
def download(request, id):
    try:
        up = Upload.objects.get(id=id)
    except Upload.DoesNotExist:
        raise Http404("Upload not found")

    return FileResponse(
        up.file.open("rb"),
        as_attachment=True,
        filename=os.path.basename(up.file.name),
    )


def pdf_to_text(filename: str) -> str:
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"Input file not found: {filename}")

    output_filename = filename + ".txt"
    subprocess.run(
        ["pdftotext", "-layout", filename, output_filename],
        check=True,
    )
    return output_filename


def _extract_first_number(pattern: str, text: str):
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    value = match.group(1).replace(",", "").strip()
    try:
        return int(value)
    except ValueError:
        return None


def _empty_process_payload():
    return {
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


@require_GET
def process(request, id):
    try:
        up = Upload.objects.get(id=id)
    except Upload.DoesNotExist:
        raise Http404("Upload not found")

    result = _empty_process_payload()

    try:
        txt_path = pdf_to_text(up.file.path)
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        return JsonResponse(result, status=200)

    result["men_applied"] = _extract_first_number(
        r"Total first-time,\s*first-year men who applied\s+([0-9,]+)", text
    )
    result["women_applied"] = _extract_first_number(
        r"Total first-time,\s*first-year women who applied\s+([0-9,]+)", text
    )
    result["another_gender_applied"] = _extract_first_number(
        r"Total first-time,\s*first-year another gender who applied\s+([0-9,]+)", text
    )
    result["unknown_gender_applied"] = _extract_first_number(
        r"Total first-time,\s*first-year unknown gender who applied\s+([0-9,]+)", text
    )
    result["men_admitted"] = _extract_first_number(
        r"Total first-time,\s*first-year men who were admitted\s+([0-9,]+)", text
    )
    result["women_admitted"] = _extract_first_number(
        r"Total first-time,\s*first-year women who were admitted\s+([0-9,]+)", text
    )
    result["another_gender_admitted"] = _extract_first_number(
        r"Total first-time,\s*first-year another gender who were admitted\s+([0-9,]+)", text
    )
    result["unknown_gender_admitted"] = _extract_first_number(
        r"Total first-time,\s*first-year unknown gender who were admitted\s+([0-9,]+)", text
    )

    result["tuition_undergraduates"] = _extract_first_number(
        r"Tuition\s*\(Undergraduates\)\s+([0-9,]+)", text
    )
    result["required_fees_undergraduates"] = _extract_first_number(
        r"Required Fees:\s*\(Undergraduates\)\s+([0-9,]+)", text
    )
    result["food_and_housing_on_campus_undergraduates"] = _extract_first_number(
        r"Food and housing\s*\(on-campus\):\s*\(Undergraduates\)\s+([0-9,]+)", text
    )
    result["housing_only_on_campus_undergraduates"] = _extract_first_number(
        r"Housing Only\s*\(on-campus\):\s*\(Undergraduates\)\s+([0-9,]+)", text
    )
    result["food_only_on_campus_meal_plan_undergraduates"] = _extract_first_number(
        r"Food Only\s*\(on-campus meal plan\):\s*\(Undergraduates\)\s+([0-9,]+)", text
    )
    result["degree_seeking_undergraduate_students"] = _extract_first_number(
        r"A\.\s*Number of degree-seeking undergraduate students\s+([0-9,]+)", text
    )
    result["applied_for_need_based_financial_aid"] = _extract_first_number(
        r"B\.\s*Number of students in line a who applied for need[- ]based financial aid\s+([0-9,]+)", text
    )
    result["determined_to_have_financial_need"] = _extract_first_number(
        r"C\.\s*Number of students in line b who were determined to have financial need\s+([0-9,]+)", text
    )
    result["awarded_any_financial_aid"] = _extract_first_number(
        r"D\.\s*Number of students in line c who were awarded any financial aid\s+([0-9,]+)", text
    )
    result["average_financial_aid_package"] = _extract_first_number(
        r"J\.\s*The average financial aid package of those in line d\s+([0-9,]+)", text
    )

    return JsonResponse(result, status=200)


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
