from django.contrib import admin

 
from.models import *
class MatchTeamDetailsAdmin(admin.TabularInline):
    model = RegisteredTeams

class PlayersPointTableAdmin(admin.TabularInline):
    model = PlayersPointTable

class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchTeamDetailsAdmin,PlayersPointTableAdmin]

admin.site.register(Match , MatchAdmin)
# admin.site.register(Tournament) # Will be replaced by TournamentAdmin
# admin.site.register(Tournament)
# admin.site.register(MatchGroup) # Will be replaced
admin.site.register(PlayersPointTable) # Consider if this needs direct tenant filtering if accessed outside MatchAdmin inlines
# admin.site.register(MatchRound) # Will be replaced by MatchRoundAdmin below
admin.site.register(RegisteredTeams) # Consider if this needs direct tenant filtering if accessed outside MatchAdmin inlines

# Tenant-aware Admin for Tournament
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('Tournament_title', 'slug', 'tenant', 'mvp_expected', 'number_of_mvp')
    list_filter = ('tenant', 'mvp_expected')
    search_fields = ('Tournament_title', 'slug', 'tenant__name')
    prepopulated_fields = {'slug': ('Tournament_title',)}

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
            # Superuser can set tenant via form if field is available, or it might be None
            pass
        elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            obj.tenant = request.user.tenant # Assign object to sub_admin's tenant
        else:
            # This case should ideally be prevented by permission checks.
            # If it's reached, it's an attempt to save without rights.
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to save this object.")
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "tenant":
            if request.user.is_superuser:
                pass # Superuser sees all tenants
            elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
                kwargs["queryset"] = Tenant.objects.filter(id=request.user.tenant.id)
                # If it's a new object, pre-select the tenant
                if not kwargs.get("initial") and not db_field.value_from_object(kwargs.get('obj')): # obj is None for add form
                     kwargs["initial"] = request.user.tenant.id
                     kwargs["disabled"] = True # Prevent changing tenant
            else: # Non-superuser without sub_admin rights or no tenant
                 kwargs["queryset"] = Tenant.objects.none()
                 kwargs["disabled"] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False # Must be a sub_admin of a tenant
        if obj is None: # List view or add view (add is covered by has_add_permission)
            return True # Can see list if sub_admin, will be filtered by get_queryset
        return obj.tenant == request.user.tenant # Can only change objects of their own tenant

    def has_delete_permission(self, request, obj=None):
        # Similar logic to has_change_permission
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None:
            return True # Can see delete buttons on list view if sub_admin
        return obj.tenant == request.user.tenant

admin.site.register(Tournament, TournamentAdmin)


# Tenant-aware Admin for MatchRound
class MatchRoundAdmin(admin.ModelAdmin):
    list_display = ('Round_title', 'Tournament', 'slug')
    search_fields = ('Round_title', 'Tournament__Tournament_title', 'Tournament__tenant__name')
    prepopulated_fields = {'slug': ('Round_title', 'Tournament')}
    list_filter = ('Tournament__tenant',)


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'tenant') and request.user.tenant:
            if request.user.sub_admin:
                return qs.filter(Tournament__tenant=request.user.tenant)
            else:
                return qs.none()
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "Tournament":
            if request.user.is_superuser:
                pass # Superuser sees all Tournaments
            elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
                kwargs["queryset"] = Tournament.objects.filter(tenant=request.user.tenant)
            else: # Non-sub_admin or no tenant
                 kwargs["queryset"] = Tournament.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        # Tournament (and thus tenant) is determined by the form selection,
        # which is already restricted by formfield_for_foreignkey.
        # No explicit tenant setting needed here if FK is correctly chosen.
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        # Allow add if user is sub_admin and there are available Tournaments for their tenant
        if hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            return Tournament.objects.filter(tenant=request.user.tenant).exists()
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None:
            return True
        return obj.Tournament.tenant == request.user.tenant

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None:
            return True
        return obj.Tournament.tenant == request.user.tenant

admin.site.register(MatchRound, MatchRoundAdmin)


# Tenant-aware Admin for MatchGroup
class MatchGroupAdmin(admin.ModelAdmin):
    list_display = ('Group_title', 'Round', 'Tournament', 'slug')
    search_fields = ('Group_title', 'Round__Round_title', 'Tournament__Tournament_title', 'Tournament__tenant__name')
    prepopulated_fields = {'slug': ('Group_title', 'Round')}
    list_filter = ('Tournament__tenant', 'Round__Tournament__tenant') # Redundant, but shows intent

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'tenant') and request.user.tenant:
            if request.user.sub_admin:
                # MatchGroup itself does not have a direct tenant link, it's via Tournament or Round.
                # Assuming Tournament is the primary link for tenancy.
                return qs.filter(Tournament__tenant=request.user.tenant)
            else:
                return qs.none()
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser:
            pass # Superuser sees all
        elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            user_tenant = request.user.tenant
            if db_field.name == "Tournament":
                 kwargs["queryset"] = Tournament.objects.filter(tenant=user_tenant)
            elif db_field.name == "Round": # MatchRound
                 kwargs["queryset"] = MatchRound.objects.filter(Tournament__tenant=user_tenant)
        else: # Non-sub_admin or no tenant
            if db_field.name == "Tournament": kwargs["queryset"] = Tournament.objects.none()
            if db_field.name == "Round": kwargs["queryset"] = MatchRound.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Tenant linkage is through selected Tournament/Round.
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            # Check if there are valid parent objects (Tournaments/Rounds) for this tenant
            return MatchRound.objects.filter(Tournament__tenant=request.user.tenant).exists() or \
                   Tournament.objects.filter(tenant=request.user.tenant).exists()
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None:
            return True
        # Check tenant via Tournament or Round. Assuming Tournament is primary.
        if obj.Tournament:
            return obj.Tournament.tenant == request.user.tenant
        if obj.Round and obj.Round.Tournament:
            return obj.Round.Tournament.tenant == request.user.tenant
        return False # Should not happen if model is structured well

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None:
            return True
        if obj.Tournament:
            return obj.Tournament.tenant == request.user.tenant
        if obj.Round and obj.Round.Tournament:
            return obj.Round.Tournament.tenant == request.user.tenant
        return False
admin.site.register(MatchGroup, MatchGroupAdmin)

# Modify MatchAdmin for tenant awareness (primarily through its ForeignKey to Tournament)
# Unregister default MatchAdmin first if it was already modified or to replace its registration
# For simplicity, assuming MatchAdmin definition is being updated here.

# Remove old registration for Match if it exists and we are redefining MatchAdmin
if admin.site.is_registered(Match):
    admin.site.unregister(Match)

class MatchAdmin(admin.ModelAdmin): # Redefining MatchAdmin or defining for the first time
    inlines = [MatchTeamDetailsAdmin,PlayersPointTableAdmin]
    list_display = ('Match_Title', 'Match_Tournament', 'Match_Round', 'Match_Group', 'Featured')
    list_filter = ('Match_Tournament__tenant', 'Featured', 'Match_Tournament', 'Match_Round')
    search_fields = ('Match_Title', 'Match_Tournament__Tournament_title', 'Match_Round__Round_title', 'Match_Group__Group_title')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'tenant') and request.user.tenant:
            if request.user.sub_admin:
                return qs.filter(Match_Tournament__tenant=request.user.tenant)
            else:
                return qs.none()
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser:
            pass # Superuser sees all
        elif hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            user_tenant = request.user.tenant
            if db_field.name == "Match_Tournament":
                kwargs["queryset"] = Tournament.objects.filter(tenant=user_tenant)
            elif db_field.name == "Match_Round":
                kwargs["queryset"] = MatchRound.objects.filter(Tournament__tenant=user_tenant)
            elif db_field.name == "Match_Group":
                kwargs["queryset"] = MatchGroup.objects.filter(Round__Tournament__tenant=user_tenant)
        else: # Non-sub_admin or no tenant
            if db_field.name == "Match_Tournament": kwargs["queryset"] = Tournament.objects.none()
            if db_field.name == "Match_Round": kwargs["queryset"] = MatchRound.objects.none()
            if db_field.name == "Match_Group": kwargs["queryset"] = MatchGroup.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Tenant linkage is through selected Match_Tournament.
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin:
            # Check if there are valid parent Tournaments for this tenant
            return Tournament.objects.filter(tenant=request.user.tenant).exists()
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None:
            return True
        return obj.Match_Tournament and obj.Match_Tournament.tenant == request.user.tenant

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not (hasattr(request.user, 'tenant') and request.user.tenant and request.user.sub_admin):
            return False
        if obj is None:
            return True
        return obj.Match_Tournament and obj.Match_Tournament.tenant == request.user.tenant

admin.site.register(Match, MatchAdmin) # Register new or redefined MatchAdmin

# Note: For RegisteredTeamsAdmin and PlayersPointTableAdmin, if they were standalone,
# they would need similar get_queryset and formfield_for_foreignkey overrides.
# As inlines, their queryset is implicitly filtered by the parent Match instance.
# However, their own ForeignKey fields (e.g., to Team for RegisteredTeams) might need
# formfield_for_foreignkey overrides if edited directly in those inlines.
# The current MatchTeamDetailsAdmin and PlayersPointTableAdmin are simple inlines without custom logic.
# Adding explicit tenant filtering to them would be safer if their related models (Team, Player)
# are not correctly filtered by context.
# For now, assuming the relation through Match is sufficient for the inline context.
# Need to import Tenant for TournamentAdmin.
from tenants.models import Tenant