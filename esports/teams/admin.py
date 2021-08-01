from re import A
from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Team_Categories)

class Team_Players_Admin(admin.TabularInline):
    model = Team_Players

class Team_Admin(admin.ModelAdmin):
    inlines = [Team_Players_Admin]

admin.site.register(Team, Team_Admin)