from http.client import OK

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup(self):
        """Страница /auth/signup/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, OK)

    def test_logout_authorized(self):
        """Страница /auth/logout/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/auth/logout/')
        self.assertEqual(response.status_code, OK)

    def test_login(self):
        """Страница /auth/login/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, OK)

    def test_password_change(self):
        """Страница по адресу /auth/password_change/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/auth/password_change/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/auth/password_change/'))

    def test_password_change_authorized(self):
        """Страница /auth/password_change/
        доступна авторизованному пользователю.
        """
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, OK)

    def test_password_reset(self):
        """Страница /auth/password_reset/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
