from http.client import NOT_FOUND, OK

from django.test import Client, TestCase

from ..models import Group, Post, User

MAIN_PAGE_URL = '/'
GROUP_PAGE_URL = '/group/test-slug/'
PROFILE_PAGE_URL = '/profile/HasNoName/'
POST_CREATE_PAGE_URL = '/create/'
UNEXISTING_PAGE_URL = '/unexisting_page/'
LOGIN_PAGE_URL = '/auth/login/'


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.POST_DETAIL_PAGE_URL = f'/posts/{cls.post.id}/'
        cls.POST_EDIT_PAGE_URL = f'/posts/{cls.post.id}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(MAIN_PAGE_URL)
        self.assertEqual(response.status_code, OK)

    def test_group_list(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get(GROUP_PAGE_URL)
        self.assertEqual(response.status_code, OK)

    def test_profile(self):
        """Страница /profile/HasNoName/ доступна любому пользователю."""
        response = self.guest_client.get(PROFILE_PAGE_URL)
        self.assertEqual(response.status_code, OK)

    def test_post_detail(self):
        """Страница /posts/1/ доступна любому пользователю."""
        response = self.guest_client.get(self.POST_DETAIL_PAGE_URL)
        self.assertEqual(response.status_code, OK)

    def test_edit_post(self):
        """Страница по адресу /posts/1/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(self.POST_EDIT_PAGE_URL, follow=True)
        self.assertRedirects(
            response, (LOGIN_PAGE_URL))

    def test_edit_post_authorized(self):
        """Страница /posts/1/edit/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(self.POST_EDIT_PAGE_URL)
        self.assertEqual(response.status_code, OK)

    def test_create_post(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(POST_CREATE_PAGE_URL, follow=True)
        self.assertRedirects(
            response, (LOGIN_PAGE_URL))

    def test_create_post_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(POST_CREATE_PAGE_URL)
        self.assertEqual(response.status_code, OK)

    def test_unexisting_page(self):
        """Страница /unexisting_page/ не существует."""
        response = self.guest_client.get(UNEXISTING_PAGE_URL)
        self.assertEqual(response.status_code, NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            MAIN_PAGE_URL: 'posts/index.html',
            GROUP_PAGE_URL: 'posts/group_list.html',
            PROFILE_PAGE_URL: 'posts/profile.html',
            self.POST_DETAIL_PAGE_URL: 'posts/post_detail.html',
            self.POST_EDIT_PAGE_URL: 'posts/create_post.html',
            POST_CREATE_PAGE_URL: 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
