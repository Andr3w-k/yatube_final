from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post, User

FOLLOW_INDEX_PAGE_URL = reverse('posts:follow_index')


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_obj = []
        cls.user_author = User.objects.create_user(username='TestAuthor')
        cls.user_follower = User.objects.create_user(username='TestFollower')
        cls.page_obj.append(Post.objects.create(
            author=cls.user_author,
            text='Пост №1 для проверки подписок главной страницы'
        ))
        cls.FOLLOW_PAGE_URL = reverse(
            'posts:profile_follow', kwargs={
                'username': cls.user_author.username
            }
        )
        cls.UNFOLLOW_PAGE_URL = reverse(
            'posts:profile_unfollow', kwargs={
                'username': cls.user_author.username
            }
        )
        cls.FOLLOW_PROFILE_PAGE_URL = reverse(
            'posts:profile', kwargs={
                'username': cls.user_author.username
            }
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_follower)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)

    def test_follow(self):
        """Проверка подписки на автора"""
        follow_count = Follow.objects.count()
        # print(f'Количество подписок = {follow_count}')
        # Проверяем, что подписок нет.
        self.assertEqual(follow_count, 0)
        # Создаем подписку через отправку POST-запроса
        response = self.authorized_client.post(
            self.FOLLOW_PAGE_URL,
        )
        # Проверили редирект
        self.assertRedirects(response, self.FOLLOW_PROFILE_PAGE_URL)
        # Проверили, что прибавилась одна подписка
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        # print('Количество постов в базе после подписки = '
        #       f'{Follow.objects.count()}')

    def test_unfollow(self):
        """Проверка отписки от автора"""
        # Создаем подписку через отправку POST-запроса
        response = self.authorized_client.post(
            self.FOLLOW_PAGE_URL,
        )
        follow_count = Follow.objects.count()
        # print(f'Количество подписок = {follow_count}')
        # Проверяем, что есть одна подписка.
        self.assertEqual(follow_count, 1)
        # Отписываемся через отправку POST-запроса
        response = self.authorized_client.post(
            self.UNFOLLOW_PAGE_URL,
        )
        # Проверили редирект
        self.assertRedirects(response, self.FOLLOW_PROFILE_PAGE_URL)
        # Проверили, что подписок нет
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        # print('Количество постов в базе после отписки = '
        #       f'{Follow.objects.count()}')

    def test_no_self_follow(self):
        """Проверка ошибки подписки пользователя на самого себя"""
        user = User.objects.create()
        constraint_name = 'prevent_self_follow'
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Follow.objects.create(user=user, author=user)

    def test_follow_post_appear(self):
        """Проверка появления нового поста на странице follow у подписчика"""
        # Создаем подписку через отправку POST-запроса
        self.authorized_client.post(self.FOLLOW_PAGE_URL)
        follow_count = Follow.objects.count()
        # print(f'Количество подписок = {follow_count}')
        # Проверяем, что есть одна подписка.
        self.assertEqual(follow_count, 1)
        # Автор, на которого офолмлена подписка создает пост
        post = Post.objects.create(
            author=self.user_author,
            text='Пост №2 для проверки подписок главной страницы'
        )
        # Проверяем появление поста на странице follow у подписчика
        response = self.authorized_client.get(FOLLOW_INDEX_PAGE_URL)
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_follow_post_dont_appear(self):
        """
        Проверка остутвия нового поста на странице follow
        у пользователя без подписки
        """
        follow_count = Follow.objects.count()
        # print(f'Количество подписок = {follow_count}')
        # Проверяем, что подписок нет.
        self.assertEqual(follow_count, 0)
        # Автор, на которого нет подписки создает пост
        post = Post.objects.create(
            author=self.user_author,
            text='Пост №3 для проверки подписок главной страницы'
        )
        # Проверяем остутстве поста на странице follow
        # у пользователя без подписки
        response = self.authorized_client.get(FOLLOW_INDEX_PAGE_URL)
        self.assertNotIn(post, response.context['page_obj'].object_list)
