"""
campus_exchange/urls.py

This is the MAIN URL configuration file for the entire project.
Django reads this file first when it receives any browser request.

Think of this as the "switchboard" — it looks at the URL and 
decides which app should handle it.

include() lets us delegate URL patterns to each app's own urls.py.
This keeps things organized — accounts handles /accounts/ URLs,
marketplace handles everything else.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin panel — available at /admin/
    # Django generates this interface automatically from your registered models
    path('admin/', admin.site.urls),

    # Accounts URLs — registration, login, logout
    # Any URL starting with /accounts/ is forwarded to accounts/urls.py
    path('accounts/', include('accounts.urls')),

    # Marketplace URLs — homepage, browse, dashboard, items, requests
    # The empty string '' means ALL other URLs go to marketplace/urls.py
    path('', include('marketplace.urls')),
]

# ------------------------------------------------------------
# MEDIA FILE SERVING (Development Only)
# In development, Django needs to serve uploaded media files itself.
# This line adds URL patterns so that /media/filename.jpg works.
# In production, a proper web server (nginx, apache) handles this.
# ------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
