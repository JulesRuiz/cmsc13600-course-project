from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from decimal import Decimal, InvalidOperation
from datetime import datetime
from zoneinfo import ZoneInfo

def time(request):
    if request.method != "GET":
        return HttpResponseBadRequest("GET required")

    now = datetime.now(ZoneInfo("America/Chicago"))
    return HttpResponse(now.strftime("%H:%M"))

def sum(request):
    if request.method != "GET":
        return HttpResponseBadRequest("GET required")

    n1 = request.GET.get("n1")
    n2 = request.GET.get("n2")

    if n1 is None or n2 is None:
        return HttpResponseBadRequest("Missing parameters")

    try:
        result = Decimal(n1) + Decimal(n2)
    except InvalidOperation:
        return HttpResponseBadRequest("Invalid numbers")

    return HttpResponse(str(result))
