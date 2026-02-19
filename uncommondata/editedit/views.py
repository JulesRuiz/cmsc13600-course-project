from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

def upload(request):
    return JsonResponse({}, status=201)

def dump_uploads(request):
    return JsonResponse({}, status=200)

def dump_data(request):
    return HttpResponse("OK", status=200)

def knockknock(request):
    return HttpResponse("Knock knock!", content_type="text/plain")

def uploads(request):
    return render(request, 'uploads.html')
