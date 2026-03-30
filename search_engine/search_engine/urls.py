"""
URL configuration for search_engine project.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('search.urls')),
]
