"""
marketplace/views.py

All views for the marketplace app.

Views are organized into sections:
  1. Public views      — no login required
  2. Item views        — managing item listings
  3. Dashboard views   — user's personal pages
  4. Lending views     — borrowing request lifecycle
  5. Exchange views    — exchange proposal lifecycle

@login_required decorator: redirects to login page if user is not authenticated.
get_object_or_404: returns the object if found, else returns a 404 page.
messages: flash messages shown to the user after an action.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Item, Category, LendingRequest, ExchangeRequest
from .forms import ItemForm, LendingRequestForm, ExchangeRequestForm


# ==============================================================
# SECTION 1 — PUBLIC VIEWS (no login required)
# ==============================================================

def home(request):
    """
    Homepage — shows featured available items and categories.
    Anyone (logged in or not) can see this page.
    """
    featured_items = Item.objects.filter(
        availability='available'
    ).select_related('owner', 'category').order_by('-created_at')[:6]

    categories = Category.objects.all()

    total_available = Item.objects.filter(availability='available').count()
    total_lenders = Item.objects.values('owner').distinct().count()

    context = {
        'featured_items': featured_items,
        'categories': categories,
        'total_available': total_available,
        'total_lenders': total_lenders,
    }
    return render(request, 'marketplace/home.html', context)


def about(request):
    """About page — describes the project."""
    return render(request, 'marketplace/about.html')


def browse_items(request):
    """
    Browse all items with search and filter functionality.

    Uses Django ORM filtering:
    - Q objects allow OR conditions (name OR description contains query)
    - .filter() chains AND conditions
    - .distinct() removes duplicates when Q is used with OR
    """
    # Start with all items
    items = Item.objects.select_related('owner', 'category').order_by('-created_at')

    # --- Search ---
    query = request.GET.get('q', '').strip()
    if query:
        # Q objects: name contains query OR description contains query
        items = items.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()

    # --- Filter: Category ---
    category_id = request.GET.get('category', '')
    if category_id:
        items = items.filter(category_id=category_id)

    # --- Filter: Listing Type ---
    listing_type = request.GET.get('type', '')
    if listing_type in ['lending', 'exchange']:
        items = items.filter(listing_type=listing_type)

    # --- Filter: Availability ---
    # Default to 'available' so browse page shows available items first
    availability = request.GET.get('availability', 'available')
    if availability:
        items = items.filter(availability=availability)

    categories = Category.objects.all()

    context = {
        'items': items,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_type': listing_type,
        'selected_availability': availability,
        'total_results': items.count(),
    }
    return render(request, 'marketplace/browse.html', context)


def item_detail(request, pk):
    """
    Single item detail page.

    Shows full item info + lending/exchange form if applicable.
    Both guests and logged-in users can view item details.
    Only logged-in users see the request forms.
    """
    item = get_object_or_404(Item, pk=pk)
    is_owner = request.user.is_authenticated and request.user == item.owner

    has_pending_lending = False
    has_pending_exchange = False

    if request.user.is_authenticated and not is_owner:
        has_pending_lending = LendingRequest.objects.filter(
            item=item, requester=request.user, status='pending'
        ).exists()
        has_pending_exchange = ExchangeRequest.objects.filter(
            requested_item=item, requester=request.user, status='pending'
        ).exists()

    context = {
        'item': item,
        'is_owner': is_owner,
        'has_pending_lending': has_pending_lending,
        'has_pending_exchange': has_pending_exchange,
        'lending_form': LendingRequestForm() if item.listing_type == 'lending' and not is_owner else None,
        'exchange_form': ExchangeRequestForm() if item.listing_type == 'exchange' and not is_owner else None,
    }
    return render(request, 'marketplace/item_detail.html', context)


# ==============================================================
# SECTION 2 — ITEM MANAGEMENT VIEWS (login required)
# ==============================================================

@login_required
def add_item(request):
    """
    Add a new item listing.
    commit=False lets us set owner before saving to database.
    """
    if request.method == 'POST':
        # request.FILES contains uploaded files (images)
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)   # Don't save yet
            item.owner = request.user        # Set the owner
            item.availability = 'available'  # New items are always available
            item.save()                      # Now save to database
            messages.success(request, f'"{item.name}" listed successfully!')
            return redirect('marketplace:my_listings')
    else:
        form = ItemForm()

    return render(request, 'marketplace/add_item.html', {'form': form})


@login_required
def edit_item(request, pk):
    """
    Edit an existing item listing.
    SERVER-SIDE check: only the owner can edit.
    """
    item = get_object_or_404(Item, pk=pk)

    # Security: check ownership at the view level, not just in the template
    if request.user != item.owner:
        messages.error(request, 'You can only edit your own listings.')
        return redirect('marketplace:item_detail', pk=pk)

    if request.method == 'POST':
        # instance=item tells the form to UPDATE this item, not create a new one
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{item.name}" updated successfully.')
            return redirect('marketplace:item_detail', pk=item.pk)
    else:
        # Pre-fill the form with current item data
        form = ItemForm(instance=item)

    return render(request, 'marketplace/edit_item.html', {'form': form, 'item': item})


@login_required
def delete_item(request, pk):
    """
    Delete an item listing.
    Only accepts POST requests (delete button is inside a form).
    """
    item = get_object_or_404(Item, pk=pk)

    if request.user != item.owner:
        messages.error(request, 'You can only delete your own listings.')
        return redirect('marketplace:my_listings')

    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'"{item_name}" has been removed from your listings.')
        return redirect('marketplace:my_listings')

    return redirect('marketplace:my_listings')


# ==============================================================
# SECTION 3 — DASHBOARD AND PROFILE VIEWS
# ==============================================================

@login_required
def dashboard(request):
    """
    Student dashboard — personal overview with statistics.
    """
    user = request.user

    total_listings = Item.objects.filter(owner=user).count()

    # Count pending requests RECEIVED (as owner)
    pending_lending_in = LendingRequest.objects.filter(owner=user, status='pending').count()
    pending_exchange_in = ExchangeRequest.objects.filter(owner=user, status='pending').count()
    total_pending_received = pending_lending_in + pending_exchange_in

    # Count pending requests SENT (as requester)
    pending_lending_out = LendingRequest.objects.filter(requester=user, status='pending').count()
    pending_exchange_out = ExchangeRequest.objects.filter(requester=user, status='pending').count()
    total_pending_sent = pending_lending_out + pending_exchange_out

    # Active lending (approved but not yet completed)
    active_lending = LendingRequest.objects.filter(owner=user, status='approved').count()

    # Recent incoming requests for the dashboard feed
    recent_lending = LendingRequest.objects.filter(
        owner=user
    ).select_related('requester', 'item').order_by('-created_at')[:4]

    recent_exchange = ExchangeRequest.objects.filter(
        owner=user
    ).select_related('requester', 'requested_item').order_by('-created_at')[:4]

    context = {
        'total_listings': total_listings,
        'total_pending_received': total_pending_received,
        'total_pending_sent': total_pending_sent,
        'active_lending': active_lending,
        'recent_lending': recent_lending,
        'recent_exchange': recent_exchange,
    }
    return render(request, 'marketplace/dashboard.html', context)


@login_required
def my_listings(request):
    """
    Shows all items listed by the logged-in user.
    """
    items = Item.objects.filter(owner=request.user).select_related('category').order_by('-created_at')
    return render(request, 'marketplace/my_listings.html', {'items': items})


@login_required
def profile(request):
    """
    Profile page showing the user's basic info, their listings,
    and their lending/borrowing history.
    """
    user = request.user
    items = Item.objects.filter(owner=user).select_related('category')
    borrowing_history = LendingRequest.objects.filter(
        requester=user
    ).select_related('item', 'owner').order_by('-created_at')
    lending_history = LendingRequest.objects.filter(
        owner=user
    ).select_related('item', 'requester').order_by('-created_at')

    context = {
        'profile_user': user,
        'items': items,
        'borrowing_history': borrowing_history,
        'lending_history': lending_history,
    }
    return render(request, 'marketplace/profile.html', context)


# ==============================================================
# SECTION 4 — LENDING REQUEST VIEWS
# ==============================================================

@login_required
def send_lending_request(request, item_pk):
    """
    Submit a borrowing request for a lending item.
    Multiple validations run before saving the request.
    """
    item = get_object_or_404(Item, pk=item_pk)

    # --- Validation checks ---
    if item.owner == request.user:
        messages.error(request, 'You cannot request your own item.')
        return redirect('marketplace:item_detail', pk=item_pk)

    if item.listing_type != 'lending':
        messages.error(request, 'This item is not listed for lending.')
        return redirect('marketplace:item_detail', pk=item_pk)

    if item.availability != 'available':
        messages.error(request, 'This item is currently not available.')
        return redirect('marketplace:item_detail', pk=item_pk)

    # Prevent duplicate pending requests
    if LendingRequest.objects.filter(item=item, requester=request.user, status='pending').exists():
        messages.warning(request, 'You already have a pending request for this item.')
        return redirect('marketplace:item_detail', pk=item_pk)

    if request.method == 'POST':
        form = LendingRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.item = item
            req.requester = request.user
            req.owner = item.owner
            req.status = 'pending'
            req.save()

            # Mark item as 'requested' so others see it is being processed
            item.availability = 'requested'
            item.save()

            messages.success(request, f'Your request for "{item.name}" has been sent to {item.owner.first_name or item.owner.username}.')
            return redirect('marketplace:lending_requests_sent')

    return redirect('marketplace:item_detail', pk=item_pk)


@login_required
def lending_requests_received(request):
    """Requests received for items owned by the logged-in user."""
    requests_list = LendingRequest.objects.filter(
        owner=request.user
    ).select_related('item', 'requester').order_by('-created_at')

    return render(request, 'marketplace/lending_requests_received.html', {
        'requests_list': requests_list
    })


@login_required
def lending_requests_sent(request):
    """Requests sent by the logged-in user."""
    requests_list = LendingRequest.objects.filter(
        requester=request.user
    ).select_related('item', 'owner').order_by('-created_at')

    return render(request, 'marketplace/lending_requests_sent.html', {
        'requests_list': requests_list
    })


@login_required
def approve_lending_request(request, pk):
    """
    Owner approves a pending lending request.
    - Sets request status to 'approved'
    - Marks item as 'lent_out'
    - Auto-rejects all other pending requests for the same item
    """
    lending_req = get_object_or_404(LendingRequest, pk=pk)

    if lending_req.owner != request.user:
        messages.error(request, "You don't have permission to approve this request.")
        return redirect('marketplace:lending_requests_received')

    if lending_req.status != 'pending':
        messages.error(request, 'Only pending requests can be approved.')
        return redirect('marketplace:lending_requests_received')

    if request.method == 'POST':
        lending_req.status = 'approved'
        lending_req.save()

        # Mark item as lent out
        lending_req.item.availability = 'lent_out'
        lending_req.item.save()

        # Reject all other pending requests for the same item
        LendingRequest.objects.filter(
            item=lending_req.item, status='pending'
        ).exclude(pk=pk).update(status='rejected')

        messages.success(request, f'Request approved. "{lending_req.item.name}" is now marked as lent out.')
        return redirect('marketplace:lending_requests_received')

    return redirect('marketplace:lending_requests_received')


@login_required
def reject_lending_request(request, pk):
    """Owner rejects a pending lending request."""
    lending_req = get_object_or_404(LendingRequest, pk=pk)

    if lending_req.owner != request.user:
        messages.error(request, "You don't have permission to reject this request.")
        return redirect('marketplace:lending_requests_received')

    if lending_req.status != 'pending':
        messages.error(request, 'Only pending requests can be rejected.')
        return redirect('marketplace:lending_requests_received')

    if request.method == 'POST':
        lending_req.status = 'rejected'
        lending_req.save()

        # If no other pending requests, make item available again
        other_pending = LendingRequest.objects.filter(
            item=lending_req.item, status='pending'
        ).exists()
        if not other_pending:
            lending_req.item.availability = 'available'
            lending_req.item.save()

        messages.success(request, 'Request rejected.')
        return redirect('marketplace:lending_requests_received')

    return redirect('marketplace:lending_requests_received')


@login_required
def cancel_lending_request(request, pk):
    """Requester cancels their own pending request."""
    lending_req = get_object_or_404(LendingRequest, pk=pk)

    if lending_req.requester != request.user:
        messages.error(request, "You can only cancel your own requests.")
        return redirect('marketplace:lending_requests_sent')

    if lending_req.status != 'pending':
        messages.error(request, 'Only pending requests can be cancelled.')
        return redirect('marketplace:lending_requests_sent')

    if request.method == 'POST':
        lending_req.status = 'cancelled'
        lending_req.save()

        # Restore item availability if no other pending requests
        other_pending = LendingRequest.objects.filter(
            item=lending_req.item, status='pending'
        ).exists()
        if not other_pending and lending_req.item.availability == 'requested':
            lending_req.item.availability = 'available'
            lending_req.item.save()

        messages.success(request, 'Your request has been cancelled.')
        return redirect('marketplace:lending_requests_sent')

    return redirect('marketplace:lending_requests_sent')


@login_required
def complete_lending_request(request, pk):
    """
    Owner marks a lending as completed (item has been returned).
    Item becomes available again.
    """
    lending_req = get_object_or_404(LendingRequest, pk=pk)

    if lending_req.owner != request.user:
        messages.error(request, "You don't have permission to complete this request.")
        return redirect('marketplace:lending_requests_received')

    if lending_req.status != 'approved':
        messages.error(request, 'Only approved requests can be marked as completed.')
        return redirect('marketplace:lending_requests_received')

    if request.method == 'POST':
        lending_req.status = 'completed'
        lending_req.save()

        # Item is returned — make it available again
        lending_req.item.availability = 'available'
        lending_req.item.save()

        messages.success(
            request,
            f'"{lending_req.item.name}" marked as returned. It is available for borrowing again.'
        )
        return redirect('marketplace:lending_requests_received')

    return redirect('marketplace:lending_requests_received')


# ==============================================================
# SECTION 5 — EXCHANGE REQUEST VIEWS
# ==============================================================

@login_required
def send_exchange_request(request, item_pk):
    """Submit an exchange proposal for an exchange-listed item."""
    item = get_object_or_404(Item, pk=item_pk)

    if item.owner == request.user:
        messages.error(request, 'You cannot propose an exchange for your own item.')
        return redirect('marketplace:item_detail', pk=item_pk)

    if item.listing_type != 'exchange':
        messages.error(request, 'This item is not listed for exchange.')
        return redirect('marketplace:item_detail', pk=item_pk)

    if item.availability != 'available':
        messages.error(request, 'This item is currently not available for exchange.')
        return redirect('marketplace:item_detail', pk=item_pk)

    if ExchangeRequest.objects.filter(
        requested_item=item, requester=request.user, status='pending'
    ).exists():
        messages.warning(request, 'You already have a pending exchange proposal for this item.')
        return redirect('marketplace:item_detail', pk=item_pk)

    if request.method == 'POST':
        form = ExchangeRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.requested_item = item
            req.requester = request.user
            req.owner = item.owner
            req.status = 'pending'
            req.save()

            item.availability = 'requested'
            item.save()

            messages.success(request, f'Your exchange proposal for "{item.name}" has been sent!')
            return redirect('marketplace:exchange_requests_sent')

    return redirect('marketplace:item_detail', pk=item_pk)


@login_required
def exchange_requests_received(request):
    """Exchange proposals received for items owned by the logged-in user."""
    requests_list = ExchangeRequest.objects.filter(
        owner=request.user
    ).select_related('requested_item', 'requester').order_by('-created_at')

    return render(request, 'marketplace/exchange_requests_received.html', {
        'requests_list': requests_list
    })


@login_required
def exchange_requests_sent(request):
    """Exchange proposals sent by the logged-in user."""
    requests_list = ExchangeRequest.objects.filter(
        requester=request.user
    ).select_related('requested_item', 'owner').order_by('-created_at')

    return render(request, 'marketplace/exchange_requests_sent.html', {
        'requests_list': requests_list
    })


@login_required
def accept_exchange_request(request, pk):
    """Owner accepts an exchange proposal."""
    exchange_req = get_object_or_404(ExchangeRequest, pk=pk)

    if exchange_req.owner != request.user:
        messages.error(request, "You don't have permission to accept this proposal.")
        return redirect('marketplace:exchange_requests_received')

    if exchange_req.status != 'pending':
        messages.error(request, 'Only pending proposals can be accepted.')
        return redirect('marketplace:exchange_requests_received')

    if request.method == 'POST':
        exchange_req.status = 'accepted'
        exchange_req.save()

        exchange_req.requested_item.availability = 'lent_out'
        exchange_req.requested_item.save()

        # Reject other pending exchange proposals for the same item
        ExchangeRequest.objects.filter(
            requested_item=exchange_req.requested_item, status='pending'
        ).exclude(pk=pk).update(status='rejected')

        messages.success(
            request,
            f'Exchange accepted! Please arrange the exchange with {exchange_req.requester.first_name or exchange_req.requester.username}.'
        )
        return redirect('marketplace:exchange_requests_received')

    return redirect('marketplace:exchange_requests_received')


@login_required
def reject_exchange_request(request, pk):
    """Owner rejects an exchange proposal."""
    exchange_req = get_object_or_404(ExchangeRequest, pk=pk)

    if exchange_req.owner != request.user:
        messages.error(request, "You don't have permission to reject this proposal.")
        return redirect('marketplace:exchange_requests_received')

    if exchange_req.status != 'pending':
        messages.error(request, 'Only pending proposals can be rejected.')
        return redirect('marketplace:exchange_requests_received')

    if request.method == 'POST':
        exchange_req.status = 'rejected'
        exchange_req.save()

        other_pending = ExchangeRequest.objects.filter(
            requested_item=exchange_req.requested_item, status='pending'
        ).exists()
        if not other_pending:
            exchange_req.requested_item.availability = 'available'
            exchange_req.requested_item.save()

        messages.success(request, 'Exchange proposal rejected.')
        return redirect('marketplace:exchange_requests_received')

    return redirect('marketplace:exchange_requests_received')


@login_required
def cancel_exchange_request(request, pk):
    """Requester cancels their own pending exchange proposal."""
    exchange_req = get_object_or_404(ExchangeRequest, pk=pk)

    if exchange_req.requester != request.user:
        messages.error(request, "You can only cancel your own proposals.")
        return redirect('marketplace:exchange_requests_sent')

    if exchange_req.status != 'pending':
        messages.error(request, 'Only pending proposals can be cancelled.')
        return redirect('marketplace:exchange_requests_sent')

    if request.method == 'POST':
        exchange_req.status = 'cancelled'
        exchange_req.save()

        other_pending = ExchangeRequest.objects.filter(
            requested_item=exchange_req.requested_item, status='pending'
        ).exists()
        if not other_pending and exchange_req.requested_item.availability == 'requested':
            exchange_req.requested_item.availability = 'available'
            exchange_req.requested_item.save()

        messages.success(request, 'Your exchange proposal has been cancelled.')
        return redirect('marketplace:exchange_requests_sent')

    return redirect('marketplace:exchange_requests_sent')


@login_required
def complete_exchange_request(request, pk):
    """Owner confirms the exchange is done. Item becomes unavailable (exchanged)."""
    exchange_req = get_object_or_404(ExchangeRequest, pk=pk)

    if exchange_req.owner != request.user:
        messages.error(request, "You don't have permission to complete this exchange.")
        return redirect('marketplace:exchange_requests_received')

    if exchange_req.status != 'accepted':
        messages.error(request, 'Only accepted exchanges can be marked as completed.')
        return redirect('marketplace:exchange_requests_received')

    if request.method == 'POST':
        exchange_req.status = 'completed'
        exchange_req.save()

        # Item is now exchanged — mark it unavailable
        exchange_req.requested_item.availability = 'unavailable'
        exchange_req.requested_item.save()

        messages.success(request, 'Exchange marked as completed!')
        return redirect('marketplace:exchange_requests_received')

    return redirect('marketplace:exchange_requests_received')
