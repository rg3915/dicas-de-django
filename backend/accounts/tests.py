# accounts/tests.py
from django.test import TestCase

from backend.accounts.models import User


class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@email.com',
            password='demodemo',
            first_name='Admin',
            last_name='Admin',
        )
        self.superuser = User.objects.create_superuser(
            email='superadmin@email.com',
            password='demodemo'
        )

    def test_user_exists(self):
        self.assertTrue(self.user)

    def test_str(self):
        self.assertEqual(self.user.email, 'admin@email.com')

    def test_return_attributes(self):
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_active',
            'is_admin',
            'is_superuser',
            'date_joined',
            'last_login',
        )

        for field in fields:
            with self.subTest():
                self.assertTrue(hasattr(User, field))

    def test_user_is_authenticated(self):
        self.assertTrue(self.user.is_authenticated)

    def test_user_is_active(self):
        self.assertTrue(self.user.is_active)

    def test_user_is_staff(self):
        self.assertFalse(self.user.is_staff)

    def test_user_is_superuser(self):
        self.assertFalse(self.user.is_superuser)

    def test_superuser_is_superuser(self):
        self.assertTrue(self.superuser.is_superuser)

    def test_user_has_perm(self):
        self.assertTrue(self.user.has_perm)

    def test_user_has_module_perms(self):
        self.assertTrue(self.user.has_module_perms)

    def test_user_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Admin Admin')

    def test_user_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), 'Admin')
