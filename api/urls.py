# api/urls.py
from django.urls import path 
from .views import NoteListCreateView, NoteRetrieveUpdateDestroyView

urlpatterns = [
    path('notes/', NoteListCreateView.as_view(), name='note-list-create'),
    path('notes/<str:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='note-retrieve-update-destroy'),
]