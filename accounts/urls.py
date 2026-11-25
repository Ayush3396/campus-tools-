"""
accounts/urls.py

URL patterns for the accounts app.
These are served under /accounts/ because of the include() in campus_exchange/urls.py.

So:
  /accounts/register/ → register_view
  /accounts/login/    → login_view
  /accounts/logout/   → logout_view
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
