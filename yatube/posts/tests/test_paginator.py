from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.client = Client()
        cls.client.force_login(cls.user)

        Post.objects.bulk_create(
            (Post(text=str(i), author=cls.user) for i in range(13)))

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""

        cache.clear()
        response = self.client.get(reverse('index'))

        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""

        response = self.client.get(reverse('index') + '?page=2')

        self.assertEqual(len(response.context.get('page').object_list), 3)
