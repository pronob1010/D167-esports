from django.test import TestCase
from django.urls import reverse

from Accounts.models import User
from matches.models import Tournament
from .models import Game, Organizer, TournamentPayment


class OrganizerFlowTests(TestCase):
    def setUp(self):
        self.game = Game.objects.filter(name="Turf Football").first()

    def _make_organizer(self, phone, username, org_name):
        user = User.objects.create_user(
            phone=phone, password="testpass123", username=username
        )
        org = Organizer.objects.create(user=user, name=org_name)
        return user, org

    def test_seed_game_exists(self):
        """The seed data migration provides Turf Football out of the box."""
        self.assertIsNotNone(self.game)

    def test_signup_creates_user_and_organizer(self):
        resp = self.client.post(
            reverse("organizer_signup"),
            {
                "username": "dhaka_league",
                "phone": "01700000001",
                "organization_name": "Dhaka Turf League",
                "contact_email": "org@example.com",
                "password1": "s3cretpass99",
                "password2": "s3cretpass99",
            },
        )
        self.assertEqual(resp.status_code, 302)
        user = User.objects.get(phone="01700000001")
        self.assertTrue(hasattr(user, "organizer"))
        self.assertEqual(user.organizer.name, "Dhaka Turf League")

    def test_create_tournament_sets_owner_and_payment(self):
        user, org = self._make_organizer("01700000002", "orgA", "Org A")
        self.client.force_login(user)
        resp = self.client.post(
            reverse("organizer_tournament_create"),
            {
                "Tournament_title": "Winter Cup",
                "game": self.game.pk,
                "format": Tournament.FORMAT_KNOCKOUT,
                "max_teams": 8,
                "entry_fee": "200",
                "about": "A friendly cup.",
            },
        )
        self.assertEqual(resp.status_code, 302)
        t = Tournament.objects.get(Tournament_title="Winter Cup")
        self.assertEqual(t.organizer, org)
        self.assertEqual(t.status, Tournament.STATUS_DRAFT)
        # Fee-per-tournament record created.
        self.assertTrue(TournamentPayment.objects.filter(tournament=t).exists())

    def test_tenant_isolation_dashboard(self):
        """Organizer A must never see Organizer B's tournaments."""
        user_a, org_a = self._make_organizer("01700000003", "orgA2", "Org A2")
        user_b, org_b = self._make_organizer("01700000004", "orgB2", "Org B2")
        Tournament.objects.create(Tournament_title="A Cup", organizer=org_a)
        Tournament.objects.create(Tournament_title="B Cup", organizer=org_b)

        self.client.force_login(user_a)
        resp = self.client.get(reverse("organizer_dashboard"))
        self.assertContains(resp, "A Cup")
        self.assertNotContains(resp, "B Cup")

    def test_tenant_isolation_cannot_access_others_tournament(self):
        """Directly requesting another organizer's tournament returns 404."""
        user_a, org_a = self._make_organizer("01700000005", "orgA3", "Org A3")
        user_b, org_b = self._make_organizer("01700000006", "orgB3", "Org B3")
        b_cup = Tournament.objects.create(Tournament_title="Secret Cup", organizer=org_b)

        self.client.force_login(user_a)
        for name in (
            "organizer_tournament_detail",
            "organizer_tournament_edit",
        ):
            resp = self.client.get(reverse(name, args=[b_cup.slug]))
            self.assertEqual(resp.status_code, 404, f"{name} leaked another tenant's data")

    def test_cannot_delete_others_tournament(self):
        user_a, org_a = self._make_organizer("01700000007", "orgA4", "Org A4")
        user_b, org_b = self._make_organizer("01700000008", "orgB4", "Org B4")
        b_cup = Tournament.objects.create(Tournament_title="B Only", organizer=org_b)

        self.client.force_login(user_a)
        resp = self.client.post(
            reverse("organizer_tournament_delete", args=[b_cup.slug])
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Tournament.objects.filter(pk=b_cup.pk).exists())

    def test_login_required(self):
        """Anonymous users are redirected away from the dashboard."""
        resp = self.client.get(reverse("organizer_dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp["Location"])
