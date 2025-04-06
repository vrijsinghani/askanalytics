from django import forms
from .models import Organization, OrganizationMembership, Role

class OrganizationForm(forms.ModelForm):
    """
    Form for creating and updating organizations.
    """
    class Meta:
        model = Organization
        fields = ['name', 'description', 'logo', 'billing_email']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class InviteUserForm(forms.Form):
    """
    Form for inviting users to an organization.
    """
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.none(),
        label="Role",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            # Get roles specific to this organization and system roles
            self.fields['role'].queryset = Role.objects.filter(
                organization=organization
            ) | Role.objects.filter(is_system_role=True)


class UpdateMembershipForm(forms.ModelForm):
    """
    Form for updating a user's membership in an organization.
    """
    class Meta:
        model = OrganizationMembership
        fields = ['role', 'status']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
