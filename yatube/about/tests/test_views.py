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

    def test_urls_uses_correct_template(self):
        """Проверка соответсвия шаблонов адресов страниц about."""

        for template, reverse_name in self.template_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse(reverse_name))

                self.assertTemplateUsed(response, template)
