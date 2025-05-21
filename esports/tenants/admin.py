from django.contrib import admin
from .models import Tenant

class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner', 'created_at')
    search_fields = ('name', 'slug', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Tenant, TenantAdmin)
