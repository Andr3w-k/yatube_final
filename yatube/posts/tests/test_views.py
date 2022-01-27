import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

MAIN_PAGE_URL = reverse('posts:index')
POST_CREATE_PAGE_URL = reverse('posts:post_create')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_obj = []
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug_1',
            description='Тестовое описание 1',
        )
        cls.page_obj.append(Post.objects.create(
            author=cls.user,
            group=cls.group_1,
            text='Тестовый пост 1'
        ))
        cls.GROUP_PAGE_URL = reverse(
            'posts:group_posts', kwargs={'slug': cls.group_1.slug}
        )
        cls.PROFILE_PAGE_URL = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )
        cls.POST_DETAIL_PAGE_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.page_obj[0].pk}
        )
        cls.POST_EDIT_PAGE_URL = reverse(
            'posts:post_edit', kwargs={'post_id': cls.page_obj[0].pk}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка URL
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            MAIN_PAGE_URL: 'posts/index.html',
            self.GROUP_PAGE_URL: 'posts/group_list.html',
            self.PROFILE_PAGE_URL: 'posts/profile.html',
            self.POST_DETAIL_PAGE_URL: 'posts/post_detail.html',
            self.POST_EDIT_PAGE_URL: 'posts/create_post.html',
            POST_CREATE_PAGE_URL: 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка контекста
    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(MAIN_PAGE_URL)
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, 'Тестовый пост 1')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(self.GROUP_PAGE_URL)
        second_object = response.context['page_obj'][0]
        post_group_0 = second_object.group
        self.assertEqual(str(post_group_0), self.group_1.title)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(self.PROFILE_PAGE_URL)
        third_object = response.context['page_obj'][0]
        post_author_0 = third_object.author
        all_posts = response.context['post_list'].count()
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(all_posts, self.user.posts.all().count())

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(self.POST_DETAIL_PAGE_URL)
        post_text_0 = response.context['post'].text
        self.assertEqual(post_text_0, self.page_obj[0].text)

    def test_create_post_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_EDIT_PAGE_URL)
        form_inital = response.context['form'].initial['text']
        self.assertEqual(form_inital, self.page_obj[0].text)
        self.assertTrue('is_edit' in response.context)

    def testcreate_post_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_CREATE_PAGE_URL)
        form_inital = response.context['form'].initial
        self.assertEqual(form_inital, {})
        self.assertFalse('is_edit' in response.context)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_obj = []
        cls.user = User.objects.create_user(username='MrNoOne')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug_1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug_2',
            description='Тестовое описание 2',
        )
        # создали 17 постов
        # 13 от первой группы
        for i in range(1, 14):
            cls.page_obj.append(Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group_1
            ))
        # 3 от второй
        for i in range(14, 17):
            cls.page_obj.append(Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group_2
            ))
        # 1 без группы
        cls.page_obj.append(Post(
            author=cls.user,
            text=f'Тестовый пост {i+1}'
        ))
        # Записали объекты Post в БД
        cls.post = Post.objects.bulk_create(cls.page_obj)
        cls.GROUP_PAGE_URL = reverse(
            'posts:group_posts', kwargs={'slug': cls.group_1.slug}
        )
        cls.PROFILE_PAGE_URL = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка пажинатора
    def test_index_page_1_list_is_10(self):
        """На страницу 1 в index выводится по 10 постов."""
        response = self.guest_client.get(MAIN_PAGE_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_page_2_list_is_7(self):
        """На страницу 2 в index выводится по 7 постов."""
        response = self.guest_client.get(MAIN_PAGE_URL + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 7)

    def test_group_list_page_1_list_is_10(self):
        """На страницу 1 в group_list выводится по 10 постов."""
        response = self.guest_client.get(self.GROUP_PAGE_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_page_2_list_is_3(self):
        """На страницу 2 в group_list выводится по 3 постa."""
        response = self.guest_client.get(self.GROUP_PAGE_URL + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_list_page_1_list_is_10(self):
        """На страницу 1 в profile выводится по 10 постов."""
        response = self.guest_client.get(self.PROFILE_PAGE_URL)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_page_2_list_is_7(self):
        """На страницу 2 в profile выводится по 7 постов."""
        response = self.guest_client.get(self.PROFILE_PAGE_URL + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 7)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.page_obj = []
        cls.user = User.objects.create_user(username='Auth')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug_1',
            description='Тестовое описание 1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug_2',
            description='Тестовое описание 2',
        )
        cls.page_obj.append(Post.objects.create(
            author=cls.user,
            group=cls.group_1,
            image=cls.uploaded,
            text='Тестовый пост с картинкой_1'
        ))
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group_1,
            image=cls.uploaded,
            text='Тестовый пост с картинкой_2')
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )
        cls.GROUP_PAGE_URL = reverse(
            'posts:group_posts', kwargs={'slug': cls.group_1.slug}
        )
        cls.PROFILE_PAGE_URL = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )
        cls.POST_DETAIL_PAGE_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка поста с группой
    def test_post_appears_on_pages(self):
        """Отображение поста на различных страницах проекта."""
        post_response = (
            MAIN_PAGE_URL,
            self.GROUP_PAGE_URL,
            self.PROFILE_PAGE_URL,
        )
        for reverse_name in post_response:
            with self.subTest(reverse_name=reverse_name):
                response_reverse = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    self.page_obj[0].text,
                    (response_reverse.context['page_obj'][1].text)
                )

    def test_post_appears_on_post_detail_page(self):
        """Отображение поста на отдельной странице поста."""
        response = self.authorized_client.get(self.POST_DETAIL_PAGE_URL)
        self.assertEqual(
            self.post.text,
            (response.context['post'].text)
        )

    def test_post_not_appears_on_page(self):
        """Пост не отображается в группе к которой не принадлежит."""
        response = self.authorized_client.get(reverse('posts:group_posts',
                                              kwargs={'slug': 'test-slug_2'}))
        all_posts = response.context['page_obj'].count(all)
        self.assertEqual(all_posts, 0)

    def test_post_appears_on_post_detail_page(self):
        """Отображение комментария на отдельной странице поста."""
        response = self.authorized_client.get(self.POST_DETAIL_PAGE_URL)
        self.assertEqual(
            self.comment.text,
            (response.context['comment'][0].text)
        )
