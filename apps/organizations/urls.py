from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    path('', views.organization_list, name='list'),
    path('switch/<uuid:org_id>/', views.switch_organization, name='switch'),
    path('settings/', views.organization_settings, name='settings'),
    path('create/', views.create_organization, name='create'),
    path('edit/<uuid:org_id>/', views.edit_organization, name='edit'),
    path('toggle-status/<uuid:org_id>/', views.toggle_organization_status, name='toggle_status'),
    path('members/', views.organization_members, name='members'),
    path('members/invite/', views.invite_member, name='invite'),
    path('members/update-role/<uuid:membership_id>/', views.update_member_role, name='update_role'),
    path('members/remove/<uuid:membership_id>/', views.remove_member, name='remove'),
    path('switcher/', views.organization_switcher, name='switcher'),
]
