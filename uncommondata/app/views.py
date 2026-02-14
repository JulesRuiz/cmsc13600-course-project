from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

def index(request):
    now_str = datetime.now().strftime("%H:%M")
    return render(request, "app/index.html", {"now_str": now_str})

def new_user_form(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    return render(request, "app/new.html")


@csrf_exempt
def create_user_api(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    email = request.POST.get("email")
    username = request.POST.get("user_name")
    password = request.POST.get("password")
    is_curator_raw = request.POST.get("is_curator")

    if not email or not username or not password or is_curator_raw is None:
        return HttpResponseBadRequest("missing fields")

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest(f"{email} email already in use")

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    login(request, user)

    return HttpResponse("success", status=201)
