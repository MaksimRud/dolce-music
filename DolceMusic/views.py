from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import render, get_object_or_404
from music_search.models import *


def home(request):
    return TemplateResponse(request, 'index.html', {})

