from django.urls import path
from . import views


urlpatterns = [
    path('contacts/', views.ContactCreateView.as_view(), name='contact-create'),  # POST — создание
    path('contacts/list/', views.ContactFilteredListView.as_view(), name='contact-list'),  # GET — список с фильтрацией
]