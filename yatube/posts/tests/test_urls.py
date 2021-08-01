from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.not_author = User.objects.create_user(username='notauthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Какое-то описание')
        cls.post = Post.objects.create(text='Текст', author=cls.author)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.not_author_auth_client = Client()
        self.authorized_client.force_login(self.author)
        self.not_author_auth_client.force_login(self.not_author)

    def test_url_exist_all_users(self):
        """Доступность страниц для любого пользователя."""

        url_names = {
            'index': reverse('index'),
            'group_name': reverse('group_name', kwargs={
                'slug': self.group.slug}),
            'profile': reverse('profile', kwargs={
                'username': self.author.username}),
            'post': reverse('post', kwargs={
                'username': self.author.username, 'post_id': self.post.id}),
        }

        for name, reverse_name in url_names.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse_name)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exist_authorized_user(self):
        """Доступность страниц для авторизованного пользователя."""

        url_names = {
            'new_post': reverse('new_post'),
            'post_edit': reverse('post_edit', kwargs={
                'username': self.author.username, 'post_id': self.post.id}),
        }

        for name, reverse_name in url_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse_name)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous(self):
        """Перенаправление анонимного пользователя
        при попытке создания/редактирования поста.
        """
        url_names = [
            reverse('new_post'),
            reverse('post_edit', kwargs={
                'username': self.author.username, 'post_id': self.post.id}),
        ]

        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                expected = f'/auth/login/?next={url}'

                self.assertRedirects(response, expected)

    def test_url_redirect_post_edit_no_author_post(self):
        """Редирект пользователя при редактировани не своего поста."""

        url = reverse('post_edit', kwargs={
            'username': self.author.username, 'post_id': self.post.id})

        response = self.not_author_auth_client.get(url, follow=True)
        expected = reverse('post', kwargs={
            'username': self.author.username,
            'post_id': self.post.id,
        })

        self.assertRedirects(response, expected)

    def test_page_not_found(self):
        """Проверка ответа сервера на отсутствие запрошенной страницы."""

        url = '/any_page/'

        response = self.authorized_client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
