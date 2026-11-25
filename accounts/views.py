"""
accounts/views.py

Handles user registration, login, and logout.

Key Django concepts used here:
- authenticate(): checks username + password against the database
- login(): creates a session for the user
- logout(): destroys the session
- messages: flash messages shown to the user (success, error)
- redirect(): sends the user to a different URL
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm


def register_view(request):
    """
    Registration view — handles both GET and POST.

    GET:  User visits /accounts/register/ → show the empty form
    POST: User submits the form → validate and create account
    """

    # If user is already logged in, no need to register again
    if request.user.is_authenticated:
        return redirect('marketplace:home')

    if request.method == 'POST':
        # Bind form to submitted data
        form = RegisterForm(request.POST)

        if form.is_valid():
            # form.save() creates and saves the User to the database
            user = form.save()
            messages.success(
                request,
                f'Account created for {user.first_name}! You can now log in.'
            )
            # POST-Redirect-GET pattern: redirect after successful POST
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please fix the errors below and try again.')

    else:
        # GET request — show empty form
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Login view.

    Uses Django's built-in AuthenticationForm which validates
    username and password automatically.
    """

    if request.user.is_authenticated:
        return redirect('marketplace:dashboard')

    if request.method == 'POST':
        # AuthenticationForm needs 'request' as first argument
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # get_user() returns the validated User object
            user = form.get_user()
            # login() saves the user's ID in the session
            login(request, user)

            display_name = user.first_name if user.first_name else user.username
            messages.success(request, f'Welcome back, {display_name}!')

            # Redirect to 'next' URL if provided (happens when @login_required redirected here)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('marketplace:dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Logout view.

    We only allow logout via POST to prevent accidental/malicious logouts
    via a crafted URL (GET request). The logout button in the navbar
    will be inside a small form with {% csrf_token %}.
    """

    if request.method == 'POST':
        # logout() clears the user's session data
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('marketplace:home')

    # If someone hits this URL with GET, just redirect home
    return redirect('marketplace:home')
