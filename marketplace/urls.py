"""
marketplace/urls.py

All URL patterns for the marketplace app.

Format: path('url/', view_function, name='url_name')
The name is used in templates: {% url 'marketplace:home' %}
and in views: redirect('marketplace:dashboard')

Dynamic URL parameters use <int:pk> syntax.
For example: path('items/<int:pk>/', views.item_detail, name='item_detail')
When a request comes in for /items/5/, Django sets pk=5 and calls item_detail(request, pk=5).
"""

from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [

    # --- Public Pages ---
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('browse/', views.browse_items, name='browse'),

    # --- Item Pages ---
    path('items/add/', views.add_item, name='add_item'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/edit/', views.edit_item, name='edit_item'),
    path('items/<int:pk>/delete/', views.delete_item, name='delete_item'),

    # --- Student Pages ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('profile/', views.profile, name='profile'),

    # --- Lending Request Actions ---
    path('items/<int:item_pk>/borrow/', views.send_lending_request, name='send_lending_request'),
    path('requests/received/', views.lending_requests_received, name='lending_requests_received'),
    path('requests/sent/', views.lending_requests_sent, name='lending_requests_sent'),
    path('requests/<int:pk>/approve/', views.approve_lending_request, name='approve_lending_request'),
    path('requests/<int:pk>/reject/', views.reject_lending_request, name='reject_lending_request'),
    path('requests/<int:pk>/cancel/', views.cancel_lending_request, name='cancel_lending_request'),
    path('requests/<int:pk>/complete/', views.complete_lending_request, name='complete_lending_request'),

    # --- Exchange Request Actions ---
    path('items/<int:item_pk>/exchange/', views.send_exchange_request, name='send_exchange_request'),
    path('exchange/received/', views.exchange_requests_received, name='exchange_requests_received'),
    path('exchange/sent/', views.exchange_requests_sent, name='exchange_requests_sent'),
    path('exchange/<int:pk>/accept/', views.accept_exchange_request, name='accept_exchange_request'),
    path('exchange/<int:pk>/reject/', views.reject_exchange_request, name='reject_exchange_request'),
    path('exchange/<int:pk>/cancel/', views.cancel_exchange_request, name='cancel_exchange_request'),
    path('exchange/<int:pk>/complete/', views.complete_exchange_request, name='complete_exchange_request'),
]
