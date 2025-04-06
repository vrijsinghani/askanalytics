from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Organization, OrganizationMembership, Role, Permission
from .forms import OrganizationForm, InviteUserForm, UpdateMembershipForm
from .utils import set_current_organization, get_current_organization
import logging

logger = logging.getLogger('organizations.views')

@login_required
def organization_list(request):
    """
    View for listing all organizations the user is a member of.
    """
    # Get all organizations the user is a member of
    memberships = OrganizationMembership.objects.filter(
        user=request.user,
        status='active'
    ).select_related('organization', 'role')
    
    # Get the current active organization
    active_org_id = request.session.get('active_organization_id')
    
    context = {
        'memberships': memberships,
        'active_org_id': active_org_id,
    }
    
    return render(request, 'organizations/list.html', context)

@login_required
def switch_organization(request, org_id):
    """
    View for switching the active organization.
    """
    # Check if the user is a member of this organization
    membership = get_object_or_404(
        OrganizationMembership, 
        user=request.user, 
        organization_id=org_id,
        status='active'
    )
    
    # Set the active organization in the session
    request.session['active_organization_id'] = str(membership.organization.id)
    request.session['active_organization_name'] = membership.organization.name
    
    # Set the organization in the context
    set_current_organization(membership.organization)
    
    # Redirect to the referring page or dashboard
    next_url = request.GET.get('next', 'dashboard')
    return redirect(next_url)

@login_required
def organization_settings(request):
    """
    View for organization settings page.
    Shows details of the current organization and allows editing.
    """
    # Get the current organization
    organization = get_current_organization()
    
    if not organization:
        messages.warning(request, "Please select an organization first.")
        return redirect('organizations:list')
    
    # Get user's membership to check permissions
    try:
        user_membership = OrganizationMembership.objects.get(user=request.user, organization=organization, status='active')
        is_owner = organization.owner == request.user
        is_admin = user_membership.role.permissions.filter(codename='manage_organization').exists()
    except OrganizationMembership.DoesNotExist:
        is_owner = False
        is_admin = False
    
    members = OrganizationMembership.objects.filter(organization=organization).select_related('user', 'role')
    
    return render(request, 'organizations/settings.html', {
        'organization': organization,
        'members': members,
        'is_owner': is_owner,
        'is_admin': is_admin,
        'active_membership': user_membership,
    })

@login_required
def edit_organization(request, org_id):
    """
    View for editing organization details.
    Only organization owners and admins can edit organization details.
    """
    organization = get_object_or_404(Organization, pk=org_id)
    
    # Check if user has permission to edit organization
    try:
        membership = OrganizationMembership.objects.get(
            user=request.user, 
            organization=organization, 
            status='active'
        )
        is_owner = organization.owner == request.user
        is_admin = membership.role.permissions.filter(codename='manage_organization').exists()
        
        if not (is_owner or is_admin):
            messages.error(request, "You don't have permission to edit this organization.")
            return redirect('organizations:settings')
            
    except OrganizationMembership.DoesNotExist:
        messages.error(request, "You are not a member of this organization.")
        return redirect('organizations:list')
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, "Organization updated successfully.")
            return redirect('organizations:settings')
    else:
        form = OrganizationForm(instance=organization)
    
    return render(request, 'organizations/edit.html', {
        'form': form,
        'organization': organization,
    })

@login_required
def create_organization(request):
    """
    View for creating a new organization.
    """
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the organization with the current user as owner
            organization = form.save(commit=False)
            organization.owner = request.user
            organization.save()
            
            # Get the Owner role
            owner_role = Role.objects.get(name='Owner', is_system_role=True)
            
            # Create membership
            OrganizationMembership.objects.create(
                organization=organization,
                user=request.user,
                role=owner_role,
                status='active',
                invitation_accepted_at=timezone.now()
            )
            
            # Set as active organization
            request.session['active_organization_id'] = str(organization.id)
            request.session['active_organization_name'] = organization.name
            
            messages.success(request, f"Organization '{organization.name}' created successfully.")
            return redirect('organizations:settings')
    else:
        form = OrganizationForm()
    
    return render(request, 'organizations/create.html', {
        'form': form,
    })

@login_required
@require_POST
def toggle_organization_status(request, org_id):
    """
    View for toggling the active status of an organization.
    Only the owner can activate/deactivate an organization.
    """
    organization = get_object_or_404(Organization, pk=org_id)
    
    # Check if user is the owner
    if organization.owner != request.user:
        messages.error(request, "Only the organization owner can change its status.")
        return redirect('organizations:settings')
    
    # Toggle status
    organization.is_active = not organization.is_active
    organization.save()
    
    status = "activated" if organization.is_active else "deactivated"
    messages.success(request, f"Organization {status} successfully.")
    
    return redirect('organizations:settings')

@login_required
def organization_members(request):
    """
    View for organization members management page.
    Lists members and allows admins to manage them.
    """
    # Get the current organization
    organization = get_current_organization()
    
    if not organization:
        messages.warning(request, "Please select an organization first.")
        return redirect('organizations:list')
    
    # Check if user has permission to view members
    try:
        active_membership = OrganizationMembership.objects.get(
            user=request.user, 
            organization=organization,
            status='active'
        )
        is_owner = organization.owner == request.user
        is_admin = active_membership.role.permissions.filter(codename__in=['manage_members', 'invite_members']).exists()
        can_view = active_membership.role.permissions.filter(codename='view_members').exists()
        
        if not (is_owner or is_admin or can_view):
            messages.error(request, "You don't have permission to view organization members.")
            return redirect('dashboard')
            
    except OrganizationMembership.DoesNotExist:
        messages.error(request, "You are not a member of this organization.")
        return redirect('organizations:list')
    
    # Get all members
    members = OrganizationMembership.objects.filter(
        organization=organization
    ).select_related('user', 'role').order_by('user__username')
    
    # Paginate members
    paginator = Paginator(members, 10)
    page_number = request.GET.get('page', 1)
    members_page = paginator.get_page(page_number)
    
    # Get available roles for dropdown
    available_roles = Role.objects.filter(
        organization=organization
    ) | Role.objects.filter(is_system_role=True)
    
    context = {
        'organization': organization,
        'members': members_page,
        'is_owner': is_owner,
        'is_admin': is_admin,
        'active_membership': active_membership,
        'available_roles': available_roles,
    }
    
    return render(request, 'organizations/members.html', context)

@login_required
def invite_member(request):
    """
    View for inviting a new member to the organization.
    """
    # Get the current organization
    organization = get_current_organization()
    
    if not organization:
        messages.warning(request, "Please select an organization first.")
        return redirect('organizations:list')
    
    # Check if user has permission to invite members
    try:
        membership = OrganizationMembership.objects.get(
            user=request.user, 
            organization=organization,
            status='active'
        )
        is_owner = organization.owner == request.user
        can_invite = membership.role.permissions.filter(codename='invite_members').exists()
        
        if not (is_owner or can_invite):
            messages.error(request, "You don't have permission to invite members.")
            return redirect('organizations:members')
            
    except OrganizationMembership.DoesNotExist:
        messages.error(request, "You are not a member of this organization.")
        return redirect('organizations:list')
    
    if request.method == 'POST':
        form = InviteUserForm(request.POST, organization=organization)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            
            # Check if user exists
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                
                # Check if already a member
                existing_membership = OrganizationMembership.objects.filter(
                    user=user,
                    organization=organization
                ).first()
                
                if existing_membership:
                    if existing_membership.status == 'active':
                        messages.warning(request, f"{email} is already a member of this organization.")
                    else:
                        # Update existing invitation
                        existing_membership.role = role
                        existing_membership.invited_by = request.user
                        existing_membership.invitation_sent_at = timezone.now()
                        existing_membership.save()
                        messages.success(request, f"Invitation to {email} has been updated.")
                else:
                    # Create new membership
                    OrganizationMembership.objects.create(
                        organization=organization,
                        user=user,
                        role=role,
                        status='invited',
                        invited_by=request.user,
                        invitation_sent_at=timezone.now()
                    )
                    messages.success(request, f"Invitation sent to {email}.")
                    
            except User.DoesNotExist:
                # User doesn't exist - would normally send an email invitation
                messages.warning(request, f"User with email {email} does not exist. Invitation would be sent via email.")
            
            return redirect('organizations:members')
    else:
        form = InviteUserForm(organization=organization)
    
    return render(request, 'organizations/invite.html', {
        'form': form,
        'organization': organization,
    })

@login_required
@require_POST
def update_member_role(request, membership_id):
    """
    View for updating a member's role.
    """
    # Get the current organization
    organization = get_current_organization()
    
    if not organization:
        messages.warning(request, "Please select an organization first.")
        return redirect('organizations:list')
    
    # Get the membership to update
    membership = get_object_or_404(
        OrganizationMembership, 
        pk=membership_id,
        organization=organization
    )
    
    # Check if user has permission to manage members
    try:
        user_membership = OrganizationMembership.objects.get(
            user=request.user, 
            organization=organization,
            status='active'
        )
        is_owner = organization.owner == request.user
        can_manage = user_membership.role.permissions.filter(codename='manage_members').exists()
        
        if not (is_owner or can_manage):
            messages.error(request, "You don't have permission to manage members.")
            return redirect('organizations:members')
            
    except OrganizationMembership.DoesNotExist:
        messages.error(request, "You are not a member of this organization.")
        return redirect('organizations:list')
    
    # Cannot change the role of the organization owner
    if membership.user == organization.owner:
        messages.error(request, "Cannot change the role of the organization owner.")
        return redirect('organizations:members')
    
    # Get the new role
    role_id = request.POST.get('role')
    role = get_object_or_404(Role, pk=role_id)
    
    # Update the membership
    membership.role = role
    membership.save()
    
    messages.success(request, f"{membership.user}'s role updated to {role.name}.")
    return redirect('organizations:members')

@login_required
@require_POST
def remove_member(request, membership_id):
    """
    View for removing a member from the organization.
    """
    # Get the current organization
    organization = get_current_organization()
    
    if not organization:
        messages.warning(request, "Please select an organization first.")
        return redirect('organizations:list')
    
    # Get the membership to remove
    membership = get_object_or_404(
        OrganizationMembership, 
        pk=membership_id,
        organization=organization
    )
    
    # Check if user has permission to manage members
    try:
        user_membership = OrganizationMembership.objects.get(
            user=request.user, 
            organization=organization,
            status='active'
        )
        is_owner = organization.owner == request.user
        can_manage = user_membership.role.permissions.filter(codename='manage_members').exists()
        
        if not (is_owner or can_manage):
            messages.error(request, "You don't have permission to manage members.")
            return redirect('organizations:members')
            
    except OrganizationMembership.DoesNotExist:
        messages.error(request, "You are not a member of this organization.")
        return redirect('organizations:list')
    
    # Cannot remove the organization owner
    if membership.user == organization.owner:
        messages.error(request, "Cannot remove the organization owner.")
        return redirect('organizations:members')
    
    # Remove the membership
    username = membership.user.username
    membership.delete()
    
    messages.success(request, f"{username} has been removed from the organization.")
    return redirect('organizations:members')
