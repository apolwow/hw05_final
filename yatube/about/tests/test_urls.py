from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.template_url_names = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech',
        }

    def test_about_url_guest_user(self):
        """Доступность страниц неавторизованому пользователю."""

        for template, reverse_name in self.template_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse(reverse_name))

                self.assertEqual(response.status_code, HTTPStatus.OK)
