from django.test import TestCase
from django.urls import reverse

from django.core import mail

from Accounts.models import User
from matches.models import Match, Tournament, TournamentRegistration, TournamentTeam
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


class FixtureViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="01800000001", password="testpass123", username="orgf"
        )
        self.org = Organizer.objects.create(user=self.user, name="Fix Org")
        self.t = Tournament.objects.create(
            Tournament_title="League Cup", organizer=self.org,
            format=Tournament.FORMAT_LEAGUE,
        )
        self.client.force_login(self.user)

    def _add_team(self, name):
        return self.client.post(
            reverse("organizer_tournament_teams", args=[self.t.slug]),
            {"name": name},
        )

    def test_add_team_and_generate_and_score(self):
        for n in ("Alpha", "Bravo", "Charlie", "Delta"):
            self._add_team(n)
        self.assertEqual(self.t.teams.count(), 4)

        resp = self.client.post(
            reverse("organizer_generate_fixtures", args=[self.t.slug])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Match.objects.filter(Match_Tournament=self.t).count(), 6)

        m = Match.objects.filter(Match_Tournament=self.t).first()
        self.client.post(
            reverse("organizer_record_score", args=[self.t.slug, m.id]),
            {"home_score": "2", "away_score": "1"},
        )
        m.refresh_from_db()
        self.assertTrue(m.is_played)
        self.assertEqual(m.home_score, 2)

        # Fixtures page renders with the generated schedule.
        resp = self.client.get(
            reverse("organizer_tournament_fixtures", args=[self.t.slug])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Matchday")

    def test_generate_requires_two_teams(self):
        self._add_team("Solo")
        self.client.post(reverse("organizer_generate_fixtures", args=[self.t.slug]))
        self.assertEqual(Match.objects.filter(Match_Tournament=self.t).count(), 0)

    def test_standings_view_renders(self):
        for n in ("Alpha", "Bravo"):
            self._add_team(n)
        self.client.post(reverse("organizer_generate_fixtures", args=[self.t.slug]))
        resp = self.client.get(
            reverse("organizer_tournament_standings", args=[self.t.slug])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Alpha")

    def test_cannot_manage_another_orgs_tournament(self):
        other_user = User.objects.create_user(
            phone="01800000099", password="testpass123", username="other"
        )
        other_org = Organizer.objects.create(user=other_user, name="Other Org")
        other_t = Tournament.objects.create(
            Tournament_title="Not Yours", organizer=other_org
        )
        # Logged in as self.user, try to touch other_org's tournament.
        for name in (
            "organizer_tournament_teams",
            "organizer_tournament_fixtures",
            "organizer_tournament_standings",
        ):
            resp = self.client.get(reverse(name, args=[other_t.slug]))
            self.assertEqual(resp.status_code, 404, name)
        resp = self.client.post(
            reverse("organizer_generate_fixtures", args=[other_t.slug])
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Match.objects.filter(Match_Tournament=other_t).count(), 0)


class PublicRegistrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="01900000001", password="testpass123", username="orgr"
        )
        self.user.email = "host@example.com"
        self.user.save()
        self.org = Organizer.objects.create(
            user=self.user, name="Reg Org", contact_email="host@example.com"
        )
        self.t = Tournament.objects.create(
            Tournament_title="Open Cup", organizer=self.org,
            status=Tournament.STATUS_OPEN, registration_open=True, max_teams=4,
        )

    def _register(self, team="Rangers"):
        return self.client.post(
            reverse("public_register", args=[self.t.slug]),
            {
                "team_name": team,
                "captain_name": "Sam",
                "captain_phone": "01712345678",
                "captain_email": "sam@example.com",
                "roster": "Sam\nAlex\nJordan",
            },
        )

    def test_public_pages_are_anonymous(self):
        # No login -> public tournament page renders.
        resp = self.client.get(reverse("public_tournament", args=[self.t.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Open Cup")

    def test_draft_tournament_not_public(self):
        draft = Tournament.objects.create(
            Tournament_title="Hidden", organizer=self.org,
            status=Tournament.STATUS_DRAFT,
        )
        resp = self.client.get(reverse("public_tournament", args=[draft.slug]))
        self.assertEqual(resp.status_code, 404)

    def test_registration_creates_pending_and_emails_organizer(self):
        resp = self._register()
        self.assertEqual(resp.status_code, 200)
        reg = TournamentRegistration.objects.get(team_name="Rangers")
        self.assertEqual(reg.status, TournamentRegistration.STATUS_PENDING)
        # Organizer gets notified.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("host@example.com", mail.outbox[0].to)

    def test_registration_blocked_when_closed(self):
        self.t.registration_open = False
        self.t.save()
        resp = self._register(team="Late")
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(TournamentRegistration.objects.filter(team_name="Late").exists())

    def test_duplicate_team_name_rejected(self):
        self._register(team="Rangers")
        resp = self._register(team="Rangers")
        self.assertEqual(resp.status_code, 200)  # re-rendered form with error
        self.assertEqual(
            TournamentRegistration.objects.filter(team_name="Rangers").count(), 1
        )

    def test_approve_creates_team_and_emails_captain(self):
        self._register(team="Rangers")
        reg = TournamentRegistration.objects.get(team_name="Rangers")
        mail.outbox.clear()
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("organizer_registration_decide", args=[self.t.slug, reg.id]),
            {"action": "approve"},
        )
        self.assertEqual(resp.status_code, 302)
        reg.refresh_from_db()
        self.assertEqual(reg.status, TournamentRegistration.STATUS_APPROVED)
        self.assertIsNotNone(reg.tournament_team)
        self.assertTrue(self.t.teams.filter(name="Rangers").exists())
        # Captain notified.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("sam@example.com", mail.outbox[0].to)

    def test_approve_respects_capacity(self):
        # Register first (while there's room), then fill the tournament so the
        # approve-time capacity gate is what blocks it.
        self._register(team="Overflow")
        reg = TournamentRegistration.objects.get(team_name="Overflow")
        for i in range(4):
            TournamentTeam.objects.create(tournament=self.t, name=f"T{i}", seed=i + 1)
        self.client.force_login(self.user)
        self.client.post(
            reverse("organizer_registration_decide", args=[self.t.slug, reg.id]),
            {"action": "approve"},
        )
        reg.refresh_from_db()
        self.assertEqual(reg.status, TournamentRegistration.STATUS_PENDING)
        self.assertFalse(self.t.teams.filter(name="Overflow").exists())

    def test_cannot_review_another_orgs_registrations(self):
        other_user = User.objects.create_user(
            phone="01900000099", password="testpass123", username="other2"
        )
        Organizer.objects.create(user=other_user, name="Other2")
        self.client.force_login(other_user)
        resp = self.client.get(
            reverse("organizer_tournament_registrations", args=[self.t.slug])
        )
        self.assertEqual(resp.status_code, 404)


class PaymentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="01600000001", password="testpass123", username="orgp"
        )
        self.org = Organizer.objects.create(user=self.user, name="Pay Org")
        self.t = Tournament.objects.create(
            Tournament_title="Paid Cup", organizer=self.org,
            status=Tournament.STATUS_DRAFT,
        )
        self.payment = TournamentPayment.objects.create(
            organizer=self.org, tournament=self.t, amount=500,
        )
        self.client.force_login(self.user)

    def test_default_gateway_is_dummy(self):
        from organizers.payments import get_gateway
        self.assertEqual(get_gateway().name, "dummy")

    def test_full_pay_flow_marks_paid(self):
        # Start -> redirect to the (dummy) gateway URL, which points at callback.
        resp = self.client.post(reverse("organizer_payment_start", args=[self.t.slug]))
        self.assertEqual(resp.status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, TournamentPayment.STATUS_INITIATED)
        self.assertIn("paymentID", resp["Location"])

        # Follow the callback the dummy gateway pointed us to.
        resp = self.client.get(resp["Location"])
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, TournamentPayment.STATUS_PAID)
        self.assertTrue(self.payment.transaction_id)
        self.assertIsNotNone(self.payment.paid_at)

    def test_failed_callback_marks_failed(self):
        url = reverse("organizer_payment_callback", args=[self.t.slug])
        resp = self.client.get(url, {"status": "failure", "paymentID": "X"})
        self.assertEqual(resp.status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, TournamentPayment.STATUS_FAILED)

    def test_zero_fee_is_waived(self):
        self.payment.amount = 0
        self.payment.save()
        self.client.post(reverse("organizer_payment_start", args=[self.t.slug]))
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, TournamentPayment.STATUS_WAIVED)

    def test_cannot_open_registration_until_paid(self):
        url = reverse("organizer_tournament_status", args=[self.t.slug])
        self.client.post(url, {"status": Tournament.STATUS_OPEN})
        self.t.refresh_from_db()
        self.assertEqual(self.t.status, Tournament.STATUS_DRAFT)
        self.assertFalse(self.t.registration_open)

    def test_can_open_registration_after_paid(self):
        self.payment.status = TournamentPayment.STATUS_PAID
        self.payment.save()
        url = reverse("organizer_tournament_status", args=[self.t.slug])
        self.client.post(url, {"status": Tournament.STATUS_OPEN})
        self.t.refresh_from_db()
        self.assertEqual(self.t.status, Tournament.STATUS_OPEN)
        self.assertTrue(self.t.registration_open)

    def test_cannot_pay_another_orgs_tournament(self):
        other_user = User.objects.create_user(
            phone="01600000099", password="testpass123", username="otherp"
        )
        Organizer.objects.create(user=other_user, name="Other P")
        self.client.force_login(other_user)
        resp = self.client.post(reverse("organizer_payment_start", args=[self.t.slug]))
        self.assertEqual(resp.status_code, 404)
