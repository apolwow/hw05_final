import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Какое-то описание')
        cls.group_test_one = Group.objects.create(
            title='Тестовый заголовок один',
            slug='test-slug-one',
            description='Группу создали для проверки')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Какой-то текст',
            author=self.user,
            group=self.group,
            image=self.uploaded
            )

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        cache.clear()
        urls_templates = {
            reverse('index'): 'posts/index.html',
            reverse('group_name', args=[self.group.slug]): 'posts/group.html',
            reverse('new_post'): 'posts/new_post.html',
            reverse('post_edit', args=[
                self.user, self.post.id]): 'posts/new_post.html',
        }

        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        """На главной старнице корректный контекст и созданный пост."""

        cache.clear()
        url = reverse('index')

        response = self.authorized_client.get(url)

        self.assertEqual(response.context['page'][0], self.post)

    def test_group_page_shows_correct_context(self):
        """Шаблон страницы группы сформирован с правильным контекстом."""

        url = reverse('group_name', kwargs={'slug': self.group.slug})

        response = self.authorized_client.get(url)

        self.assertEqual(response.context['page'][0], self.post)

    def test_new_page_shows_correct_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""

        url = reverse('new_post')
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        response = self.authorized_client.get(url)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]

                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""

        url = reverse('post_edit', kwargs={
            'username': self.user.username, 'post_id': self.post.id})
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        response = self.authorized_client.get(url)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]

                self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон профайла пользователя сформирован с правильным котекстом."""

        url = reverse('profile', kwargs={'username': self.user.username})

        response = self.authorized_client.get(url)

        self.assertEqual(response.context['page'][0], self.post)

    def test_post_view_page_shows_correct_context(self):
        """Шаблон отдельного поста сформирован с правильным контекстом."""

        url = reverse('post', kwargs={
            'username': self.user.username, 'post_id': self.post.id
        })

        response = self.authorized_client.get(url)

        self.assertEqual(response.context['post'], self.post)

    def test_group_page_shows_new_post(self):
        """Пост отображается на странице выбранной группы."""

        url = reverse('group_name', kwargs={'slug': self.group.slug})

        response = self.authorized_client.get(url)

        self.assertTrue(self.post in response.context['page'])

    def test_group_one_page_not_shows_new_post(self):
        """Пост не попал в группу, для которой не был предназначен."""

        url = reverse('group_name', kwargs={'slug': self.group_test_one.slug})

        response = self.authorized_client.get(url)

        self.assertTrue(self.post not in response.context['page'])

    def test_works_cache_index_page(self):
        """Кэширование страницы index."""

        url = reverse('index')

        response = self.guest_client.get(url)
        Post.objects.create(text='Поста в кэше нет.', author=self.user)

        self.assertEqual(response.content, self.guest_client.get(url).content)
        cache.clear()
        self.assertNotEqual(
            response.content, self.guest_client.get(url).content
        )
