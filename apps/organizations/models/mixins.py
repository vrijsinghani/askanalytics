from django.db import models
import logging

logger = logging.getLogger('organizations.models')

class OrganizationModelManager(models.Manager):
    """
    A model manager that automatically filters querysets based on the user's active organization.
    This ensures organization isolation at the query level without relying on view-level filtering.
    """
    def get_queryset(self):
        from ..utils import get_current_user, get_current_organization
        
        queryset = super().get_queryset()
        user = get_current_user()
        
        # Superusers can see all records when needed
        if user and user.is_superuser:
            return queryset
            
        # Try to get from context directly first (most reliable)
        org = get_current_organization()
        if org:
            logger.debug(f"Filtering queryset by organization from context: {org.id}")
            return queryset.filter(organization_id=org.id)
            
        # If no organization context, return empty queryset for security
        logger.warning("No organization context found, returning empty queryset")
        return queryset.none()


class OrganizationUnfilteredManager(models.Manager):
    """
    A model manager that does not filter by organization.
    This should only be used in admin contexts or by superusers.
    """
    def get_queryset(self):
        return super().get_queryset()


class OrganizationModelMixin(models.Model):
    """
    Abstract model mixin that enforces organization-based access control.
    Models that inherit this will automatically be scoped to an organization.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )
    
    # Organization-filtered manager - THIS IS NOW THE DEFAULT
    objects = OrganizationModelManager()
    
    # Unfiltered manager - use this explicitly only when needed
    unfiltered_objects = OrganizationUnfilteredManager()
    
    class Meta:
        abstract = True
