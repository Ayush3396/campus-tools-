"""
marketplace/models.py

This file defines the database structure for our application.
Each class here becomes a table in the SQLite database.

Django ORM (Object Relational Mapper) lets us work with the database
using Python code instead of raw SQL queries.
"""

from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------------------------------
# CATEGORY MODEL
# Stores item categories like "Books & Notes", "Electronics" etc.
# Admin will manage these from the Django Admin panel.
# ---------------------------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    # blank=True means this field is not required in forms
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'  # Fixes "Categorys" in admin
        ordering = ['name']                 # Always show alphabetically

    def __str__(self):
        # This is what shows up in dropdowns and admin lists
        return self.name


# ---------------------------------------------------------------
# ITEM MODEL
# Represents a single item listing posted by a student.
# ---------------------------------------------------------------
class Item(models.Model):

    # --- CHOICES ---
    # Django choices are tuples: (stored_value, display_label)
    # The first value is what goes into the database.
    # The second value is what the user sees in forms.

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]

    LISTING_TYPE_CHOICES = [
        ('lending', 'Lending'),
        ('exchange', 'Exchange'),
    ]

    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('requested', 'Requested'),
        ('lent_out', 'Lent Out'),
        ('unavailable', 'Unavailable'),
    ]

    # --- FIELDS ---

    # ForeignKey creates a many-to-one relationship.
    # on_delete=CASCADE means: if the user is deleted, delete their items too.
    # related_name='items' lets us do user.items.all() in views.
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='items'
    )

    name = models.CharField(max_length=200)
    description = models.TextField()

    # on_delete=SET_NULL means: if category is deleted, set category to null.
    # null=True allows NULL in database. blank=True allows empty form submission.
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='items'
    )

    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default='available'
    )

    # ImageField stores the file path in the database.
    # upload_to='items/' means uploaded files go into media/items/
    # blank=True, null=True makes it optional
    image = models.ImageField(upload_to='items/', blank=True, null=True)

    # auto_now_add=True: automatically set when record is first created
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now=True: automatically updated every time the record is saved
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Newest items first

    def __str__(self):
        return f"{self.name} — by {self.owner.username}"

    def get_condition_display_class(self):
        """Returns a CSS class name based on condition for styling."""
        return {
            'new': 'badge-new',
            'like_new': 'badge-like-new',
            'good': 'badge-good',
            'fair': 'badge-fair',
        }.get(self.condition, '')

    def get_availability_display_class(self):
        """Returns a CSS class name based on availability for styling."""
        return {
            'available': 'badge-available',
            'requested': 'badge-requested',
            'lent_out': 'badge-lent-out',
            'unavailable': 'badge-unavailable',
        }.get(self.availability, '')


# ---------------------------------------------------------------
# LENDING REQUEST MODEL
# Created when Student B wants to borrow Student A's item.
# ---------------------------------------------------------------
class LendingRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # The item being requested
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='lending_requests'
    )

    # The student who sent the request
    # related_name='sent_lending_requests' → user.sent_lending_requests.all()
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_lending_requests'
    )

    # The student who owns the item
    # related_name='received_lending_requests' → user.received_lending_requests.all()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_lending_requests'
    )

    # Why the requester needs the item
    message = models.TextField()

    # How long they need it, e.g. "3 days", "1 week"
    duration = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requester.username} requests '{self.item.name}' [{self.status}]"


# ---------------------------------------------------------------
# EXCHANGE REQUEST MODEL
# Created when Student B proposes to swap their item for Student A's item.
# ---------------------------------------------------------------
class ExchangeRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # The item the requester wants
    requested_item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='exchange_requests'
    )

    # Student proposing the exchange
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_exchange_requests'
    )

    # Student who owns the item being requested
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_exchange_requests'
    )

    # Details about what the requester is offering in return
    offered_item_name = models.CharField(max_length=200)
    offered_item_description = models.TextField()

    # Optional extra message
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requester.username} offers '{self.offered_item_name}' for '{self.requested_item.name}' [{self.status}]"
