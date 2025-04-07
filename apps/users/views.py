from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from apps.users.models import Profile
from apps.users.forms import ProfileForm, QuillFieldForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from rest_framework.authtoken.models import Token

# Create your views here.


@login_required(login_url='/accounts/login/basic-login/')
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = QuillFieldForm(instance=profile)
    if request.method == 'POST':

        if request.POST.get('email'):
            request.user.email = request.POST.get('email')
            request.user.save()

        for attribute, value in request.POST.items():
            if attribute == 'csrfmiddlewaretoken':
                continue

            setattr(profile, attribute, value)
            profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect(request.META.get('HTTP_REFERER'))

    context = {
        'segment': 'profile',
        'parent': 'apps',
        'form': form
    }
    return render(request, 'pages/apps/user-profile.html', context)


def upload_avatar(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        profile.avatar = request.FILES.get('avatar')
        profile.save()
        messages.success(request, 'Avatar uploaded successfully')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def change_mode(request):
    """
    Toggle dark mode for the current user.
    This view is called via AJAX from the dark mode toggle in the configurator.
    """
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user=request.user)
        dark_mode = request.POST.get('dark_mode', 'false')
        profile.dark_mode = dark_mode.lower() == 'true'
        profile.save()

        return JsonResponse({
            'success': True,
            'dark_mode': profile.dark_mode
        })

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)


def change_password(request):
    user = request.user
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password == confirm_new_password:
            if check_password(request.POST.get('current_password'), user.password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully')
            else:
                messages.error(request, "Old password doesn't match!")
        else:
            messages.error(request, "Password doesn't match!")

    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/accounts/login/basic-login/')
def change_mode(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.dark_mode:
        profile.dark_mode = False
    else:
        profile.dark_mode = True

    profile.save()

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def api_token(request):
    """
    View for displaying and managing API tokens.
    """
    # Get or create token
    token, created = Token.objects.get_or_create(user=request.user)

    context = {
        'segment': 'api_token',
        'parent': 'apps',
        'token': token.key,
        'created': token.created,
    }
    return render(request, 'pages/apps/api-token.html', context)


@login_required
def regenerate_token(request):
    """
    View for regenerating API token.
    """
    if request.method == 'POST':
        # Delete existing token
        Token.objects.filter(user=request.user).delete()
        # Create new token
        token = Token.objects.create(user=request.user)
        messages.success(request, 'API token regenerated successfully')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'token': token.key,
                'created': token.created.isoformat(),
                'message': 'API token regenerated successfully'
            })

    return redirect('users:api_token')