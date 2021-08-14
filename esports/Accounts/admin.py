from django.contrib import admin

from.models import *

class UserProfileAdmin(admin.StackedInline):
    model = UserProfile

class UserSocialMediaAdmin(admin.StackedInline):
    model = UserSocialMedia
class shareMediaOrTextAdmin(admin.StackedInline):
    model = shareMediaOrText
class SubAdminCustom(admin.ModelAdmin):
    inlines = [UserProfileAdmin, UserSocialMediaAdmin, shareMediaOrTextAdmin]

admin.site.register(User, SubAdminCustom)

# admin.site.register(User)