from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User

MAIN_PAGE_URL = reverse('posts:index')


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_obj = []
        cls.user = User.objects.create_user(username='HasNoName')
        cls.page_obj.append(Post.objects.create(
            author=cls.user,
            text='Пост для проверки кэша главной страницы'
        ))

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверка работы кэша гавной страницы index."""
        posts_count = Post.objects.count()
        response = self.client.get(MAIN_PAGE_URL)
        content = response.content
        # print(content.decode())
        # print(f'ID поста = {self.page_obj[0].id}')
        # print(f'Количество постов в базе = {posts_count}')
        # Проверяем, что пост есть в БД
        self.assertEqual(posts_count, 1)
        # Удаляем пост
        Post.objects.filter(id=1).delete()
        # Проверяем отуствие поста в БД
        self.assertNotEqual(posts_count, Post.objects.count())
        # print(f'Количество постов в базе после удаления поста = {Post.objects.count()}')
        # Проверям доступyность поста на странице из кеша
        self.assertEqual(content, self.client.get(MAIN_PAGE_URL).content)
        # Очищаем кеш
        cache.clear()
        # print('Cleared cache')
        # Кэш очищен, проверяем, что на странице нет поста
        self.assertNotEqual(content, self.client.get(MAIN_PAGE_URL).content)
        # print(self.client.get(MAIN_PAGE_URL).content.decode())
