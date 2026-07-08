from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
