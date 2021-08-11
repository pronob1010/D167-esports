from django.contrib import admin

from.models import *



class UserSocialMediaAdmin(admin.StackedInline):
    model = UserSocialMedia
class shareMediaOrTextAdmin(admin.StackedInline):
    model = shareMediaOrText
class SubAdminCustom(admin.ModelAdmin):
    inlines = [UserSocialMediaAdmin, shareMediaOrTextAdmin]

admin.site.register(User, SubAdminCustom)

# admin.site.register(User)