from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Beneficiary


class AdminTemplateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="strong-pass123",
            is_staff=True,
            is_superuser=True,
        )

    def test_admin_index_renders_without_template_error(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Role-aware Admin Dashboard")


class BeneficiaryDeleteTests(TestCase):
    def test_owner_can_delete_their_own_beneficiary_profile(self):
        owner = get_user_model().objects.create_user(
            username="owner",
            email="owner@example.com",
            password="strong-pass123",
        )
        beneficiary = Beneficiary.objects.create(
            user=owner,
            full_name="Owner Person",
            gender="male",
            phone1="123456789",
            address="Somewhere",
            family_size=2,
            category="other",
            occupation="Worker",
        )

        self.client.force_login(owner)
        response = self.client.post(reverse("beneficiary_delete", args=[beneficiary.id]), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("register"))
        self.assertContains(response, "Your account and profile were deleted successfully. Please register again.")
        self.assertFalse(Beneficiary.objects.filter(id=beneficiary.id).exists())
        self.assertFalse(get_user_model().objects.filter(id=owner.id).exists())
        self.assertFalse(self.client.session.get('_auth_user_id'))
