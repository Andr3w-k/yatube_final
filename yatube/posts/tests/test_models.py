from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        expected_object_name_group = group.title
        expected_object_name_post = post.text[:15]
        self.assertEqual(expected_object_name_group, str(group))
        self.assertEqual(expected_object_name_post, str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        post = PostModelTest.post
        field_verboses_group = {
            'title': 'Заголовок',
            'description': 'Описание',
        }
        field_verboses_post = {
            'author': 'Автор',
            'text': 'Текст поста',
            'group': 'Группа',
            'pub_date': 'Дата публикации',
        }
        for value, expected in field_verboses_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)
        for value, expected in field_verboses_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        post = PostModelTest.post
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': ('Введите человеко-понятный URL. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Введите описание группы',
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        post = PostModelTest.post
        field_help_texts_group = {
            'title': 'Введите название группы',
            'slug': ('Введите человеко-понятный URL. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Введите описание группы',
        }
        field_help_texts_post = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
        for value, expected in field_help_texts_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
