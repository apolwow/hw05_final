from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test', password='secret')
        cls.post = Post.objects.create(text='Тестовый текст', author=cls.user)

    def test_object_name_is_text_field(self):
        """__str__ post - это строчка с содержимым post.text"""

        post = PostModelTest.post

        expected_object_name = post.text[:15]

        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='Группа для тестирования')

    def test_object_name_is_title_field(self):
        """"__str__ group - это строчка с содержимым group.title"""

        group = GroupModelTest.group

        expected_objects_name = group.title

        self.assertEqual(expected_objects_name, str(group))
