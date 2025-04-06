from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Organization, OrganizationMembership, Role, Permission

User = get_user_model()

@receiver(post_save, sender=User)
def create_personal_organization(sender, instance, created, **kwargs):
    """
    Create a personal organization for new users.
    """
    if created:
        # Check if system roles exist, create them if not
        ensure_system_roles_exist()
        
        # Create a personal organization for the user
        try:
            org = Organization.objects.create(
                name=f"{instance.get_full_name() or instance.username}'s Organization",
                owner=instance,
                is_active=True
            )
            
            # Get the Owner role
            owner_role = Role.objects.get(name='Owner', is_system_role=True)
            
            # Create membership
            OrganizationMembership.objects.create(
                organization=org,
                user=instance,
                role=owner_role,
                status='active',
                invitation_accepted_at=timezone.now()
            )
        except Exception as e:
            # Log the error but don't prevent user creation
            import logging
            logger = logging.getLogger('organizations.signals')
            logger.error(f"Error creating personal organization for user {instance.username}: {e}")


def ensure_system_roles_exist():
    """
    Ensure that system roles and permissions exist.
    """
    # Create system permissions if they don't exist
    permissions = {
        'manage_organization': 'Manage Organization',
        'invite_members': 'Invite Members',
        'manage_members': 'Manage Members',
        'view_members': 'View Members',
        'manage_clients': 'Manage Clients',
        'view_clients': 'View Clients',
        'manage_projects': 'Manage Projects',
        'view_projects': 'View Projects',
    }
    
    for codename, name in permissions.items():
        Permission.objects.get_or_create(
            codename=codename,
            defaults={
                'name': name,
                'is_system_permission': True
            }
        )
    
    # Create system roles if they don't exist
    roles = {
        'Owner': ['manage_organization', 'invite_members', 'manage_members', 'view_members', 
                 'manage_clients', 'view_clients', 'manage_projects', 'view_projects'],
        'Admin': ['invite_members', 'manage_members', 'view_members', 
                 'manage_clients', 'view_clients', 'manage_projects', 'view_projects'],
        'Member': ['view_members', 'view_clients', 'view_projects'],
        'Guest': ['view_projects'],
    }
    
    for role_name, permission_codes in roles.items():
        role, created = Role.objects.get_or_create(
            name=role_name,
            is_system_role=True,
            defaults={'description': f'System role: {role_name}'}
        )
        
        # Add permissions to the role
        permissions_to_add = Permission.objects.filter(codename__in=permission_codes)
        role.permissions.add(*permissions_to_add)
