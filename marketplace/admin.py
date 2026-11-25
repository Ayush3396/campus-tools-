"""
marketplace/admin.py

Registers our models with Django Admin.
After registering, the admin can view, create, edit, and delete
records for each model directly from the /admin/ panel.

@admin.register(ModelName) is a decorator — a shortcut for
admin.site.register(ModelName, ModelNameAdmin)
"""

from django.contrib import admin
from .models import Category, Item, LendingRequest, ExchangeRequest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Columns shown in the list view
    list_display = ('name', 'description')
    # Adds a search box that searches these fields
    search_fields = ('name',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'listing_type', 'availability', 'condition', 'created_at')
    # Adds filter sidebar on the right
    list_filter = ('listing_type', 'availability', 'condition', 'category')
    search_fields = ('name', 'description', 'owner__username')
    # These fields are shown but cannot be edited (they are auto-set)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(LendingRequest)
class LendingRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'requester', 'owner', 'duration', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('item__name', 'requester__username', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = ('requested_item', 'requester', 'owner', 'offered_item_name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('requested_item__name', 'requester__username')
    readonly_fields = ('created_at', 'updated_at')
