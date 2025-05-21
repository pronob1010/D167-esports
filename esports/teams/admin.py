
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(TeamGroup) # Assuming TeamGroup remains global as per current model structure

# Inline for TeamPlayers within TeamAdmin
class TeamPlayersAdmin(admin.TabularInline):
    model = TeamPlayers
    # Potentially add formfield_for_foreignkey for 'player' if players needed tenant scoping,
    # but players are assumed global.

# TeamAdmin: Tenant-aware
class TeamAdmin(admin.ModelAdmin):
    inlines = [TeamPlayersAdmin,]
    list_display = ('TeamName', 'Team_Group', 'tenant', 'slug') # Added tenant
    list_filter = ('tenant', 'Team_Group') # Added tenant
    search_fields = ('TeamName', 'slug', 'tenant__name')
    prepopulated_fields = {'slug': ('TeamName',)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'tenant') and request.user.tenant:
            if request.user.sub_admin: # User is a sub_admin for their tenant
                return qs.filter(tenant=request.user.tenant)
            else: # User is in a tenant but not a sub_admin
                return qs.none() # No access or read-only with empty list
        return qs.none() # Not superuser, not assigned to a tenant

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            # Superuser can set tenant via form if field is available
            # If tenant field is disabled for them, it won't be in form.cleaned_data
            # If 'tenant' is in form.fields and not disabled, superuser choice is respected.
            # If obj.tenant is None and 'tenant' is not in form or disabled, it remains None (or DB default if any)
            # This behavior depends on how 'tenant' field is handled in formfield_for_foreignkey for superuser.
            # Assuming superuser can select or it's set if field is present.
             pass # Tenant set by form if available, or obj.tenant keeps its value.
        elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            obj.tenant = request.user.tenant # Assign object to sub_admin's tenant
        else:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to save this Team object.")
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tenant":
            if request.user.is_superuser:
                # Superuser sees all tenants. Default queryset is fine.
                pass
            elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
                kwargs["queryset"] = Tenant.objects.filter(id=request.user.tenant.id)
                # For a new object, pre-select the tenant and disable the field for sub_admins
                if not kwargs.get("initial") and not getattr(kwargs.get('obj'), 'pk', None) : # obj is None or has no pk for add form
                     kwargs["initial"] = request.user.tenant.id
                     kwargs["disabled"] = True 
            else: # Non-superuser without sub_admin rights or no tenant
                 kwargs["queryset"] = Tenant.objects.none()
                 kwargs["disabled"] = True # Also disable if no valid options
        # Team_Group is assumed global. If it were tenant-specific, similar logic would apply.
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        # User must be a sub_admin of a tenant to add a Team
        return hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False # Must be a sub_admin of a tenant
        if obj is None: # List view (get_queryset handles filtering) or add view (covered by has_add_permission)
            return True
        return obj.tenant == request.user.tenant # Can only change teams of their own tenant

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None: # List view
            return True
        return obj.tenant == request.user.tenant # Can only delete teams of their own tenant

admin.site.register(Team, TeamAdmin)


# Inlines for CentralTeam Admin
class CentralTeamAchievementAdmin(admin.StackedInline):
    model = CentralTeamAchievement
    extra = 1

class OtherLineUpAdmin(admin.StackedInline):
    model = OtherLineUp
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filter 'team' ForeignKey in OtherLineUp inline to teams of the current user's tenant
        if db_field.name == "team": # ForeignKey to Team model
            if not request.user.is_superuser and hasattr(request.user, 'tenant') and request.user.tenant:
                kwargs["queryset"] = Team.objects.filter(tenant=request.user.tenant)
            elif not request.user.is_superuser: # Non-superuser without a tenant
                 kwargs["queryset"] = Team.objects.none()
            # If superuser, default queryset (all teams) is fine.
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# CentralTeamAdmin: Tenant-aware (via BS_team)
class CentralTeamAdmin(admin.ModelAdmin): # Renamed from CentralTeamAchievementBlock for clarity
    inlines = [OtherLineUpAdmin, CentralTeamAchievementAdmin]
    list_display = ('BS_team', 'game', 'get_tenant', 'slug')
    search_fields = ('BS_team__TeamName', 'game', 'BS_team__tenant__name')
    list_filter = ('BS_team__tenant', 'game') # Filter by tenant of the BS_team

    def get_tenant(self, obj):
        return obj.BS_team.tenant
    get_tenant.short_description = 'Tenant'
    get_tenant.admin_order_field = 'BS_team__tenant'


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'tenant') and request.user.tenant:
            if request.user.sub_admin: # User is a sub_admin for their tenant
                return qs.filter(BS_team__tenant=request.user.tenant)
            else: # User is in a tenant but not a sub_admin
                return qs.none()
        return qs.none() # Not superuser, not assigned to a tenant

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "BS_team": # ForeignKey to Team model
            if request.user.is_superuser:
                # Superuser sees all Teams. Default queryset is fine.
                pass
            elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
                # Sub_admin sees only teams from their tenant
                kwargs["queryset"] = Team.objects.filter(tenant=request.user.tenant)
            else: # Non-sub_admin or no tenant
                 kwargs["queryset"] = Team.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # save_model for CentralTeam: Tenant is implicitly set via BS_team.
    # Ensure BS_team choice is restricted.
    def save_model(self, request, obj, form, change):
        # The tenant context is derived from obj.BS_team.
        # If BS_team is selected from a list already filtered for the sub_admin's tenant,
        # then the CentralTeam will correctly belong to that tenant's ecosystem.
        # No need to directly set a tenant field on CentralTeam if it doesn't have one.
        # Validation: Ensure the selected BS_team (if any) belongs to the sub_admin's tenant.
        if not request.user.is_superuser and hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            if obj.BS_team and obj.BS_team.tenant != request.user.tenant:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("You cannot assign this CentralTeam to a team from another tenant.")
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        # User must be a sub_admin and there must be teams in their tenant to assign to BS_team
        if hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            return Team.objects.filter(tenant=request.user.tenant).exists()
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None: # List view
            return True
        # CentralTeam's tenant is determined by its BS_team's tenant
        return obj.BS_team and obj.BS_team.tenant == request.user.tenant

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None: # List view
            return True
        return obj.BS_team and obj.BS_team.tenant == request.user.tenant

admin.site.register(CentralTeam, CentralTeamAdmin)

# Need to import Tenant for TeamAdmin
from tenants.models import Tenant
