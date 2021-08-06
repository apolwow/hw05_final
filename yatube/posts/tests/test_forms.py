import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Краткое описание'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Форма создает запись в Post с изображением."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок',
            'group': self.group.id,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=form_data['group'],
                image='posts/small.gif',
            ).exists()
        )

    def test_create_post_choice_group(self):
        """Форма создает пост с группой и
        без нее, редиректит на главную страницу.
        """
        forms = {
            'in_group': {'text': 'В группе', 'group': self.group.id},
            'not_in_group': {'text': 'Не в группе'},
        }

        for data, value in forms.items():
            with self.subTest(data=data):
                post_count = Post.objects.count()
                response = self.authorized_client.post(
                    reverse('new_post'),
                    data=value,
                    follow=True
                )

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertRedirects(response, reverse('index'))
                self.assertEqual(Post.objects.count(), post_count + 1)
                self.assertTrue(
                    Post.objects.filter(
                        text=value.get('text'),
                        author=self.user,
                        group=value.get('group'),
                    ).exists()
                )

    def test_post_edit_change_text_and_group(self):
        """Форма редактирует пост и редиректит на запись."""

        self.post = Post.objects.create(text='Текст', author=self.user)
        url = reverse('post', kwargs={
            'username': self.user.username, 'post_id': self.post.id,
        })
        forms = {
            'change_text': {'text': 'Изменил текст'},
            'change_group': {'text': 'Текст', 'group': self.group.id},
        }

        for data, value in forms.items():
            with self.subTest(data=data):
                response = self.authorized_client.post(
                    reverse('post_edit', kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id,
                    }),
                    data=value,
                    follow=True
                )
                self.post.refresh_from_db()

                self.assertRedirects(response, url)
                self.assertEqual(self.post.text, value.get('text'))
                self.assertTrue(
                    Post.objects.filter(
                        text=value.get('text'),
                        author=self.user,
                        group=value.get('group'),
                    ).exists()
                )
