from django.contrib import admin

from .models import Game, Organizer, TournamentPayment


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "default_team_size", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "contact_email", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_email", "user__phone")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TournamentPayment)
class TournamentPaymentAdmin(admin.ModelAdmin):
    list_display = ("tournament", "organizer", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("tournament__Tournament_title", "organizer__name")
