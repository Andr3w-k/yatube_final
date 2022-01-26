import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post, User

MAIN_PAGE_URL = reverse('posts:index')
POST_CREATE_PAGE_URL = reverse('posts:post_create')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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
            text='Тестовая текст',
            group=cls.group,
        )
        cls.form = PostForm()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.PROFILE_PAGE_URL = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )
        cls.POST_EDIT_PAGE_URL = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.pk}
        )
        cls.POST_DETAIL_PAGE_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.pk}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый текст 1',
            'group': self.group.id,
            'image': self.uploaded,
        }
        # Отправили POST-запрос
        response = self.authorized_client.post(
            POST_CREATE_PAGE_URL,
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.PROFILE_PAGE_URL)
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создан пост
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст 1',
                group=self.group.id,
            ).exists()
        )
        self.assertIsNotNone(self.post.image)

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Текст поста для теста 2',
            'group': self.group.id,
        }
        # Отправили POST-запрос
        response = self.authorized_client.post(
            self.POST_EDIT_PAGE_URL,
            data=form_data,
            follow=True
        )
        # Проверили редирект
        self.assertRedirects(response, self.POST_DETAIL_PAGE_URL)
        # Проверили, что пост обновлен
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста для теста 2',
                group=self.group.id,
            ).exists()
        )
        self.assertIsNotNone(self.post.image)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая текст',
        )
        cls.form = CommentForm()
        cls.ADD_COMMENT_PAGE_URL = reverse(
            'posts:add_comment', kwargs={'post_id': cls.post.pk}
        )
        cls.POST_DETAIL_PAGE_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.pk}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Валидная форма создает комментарий к посту."""
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый комментарий',
            'post': self.post
        }
        # Отправили POST-запрос
        response = self.authorized_client.post(
            self.ADD_COMMENT_PAGE_URL,
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.POST_DETAIL_PAGE_URL)
        # Проверяем, что создан комментарий
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
                post=self.post,
            ).exists()
        )
