from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import Post


User = get_user_model()


class TaskPostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="HasNoName")

        cls.post = Post.objects.create(
            author=cls.user,
            pub_date=timezone.now(),
            text="Тестовый текст",
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cant_create_empty_post(self):
        """Проверка формы: поле с текстом не может быть пустым"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "",
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(response, "form", "text", "Обязательное поле.")
        self.assertEqual(response.status_code, 200)

    def test_can_create_post(self):
        """Проверка форм: создание поста должно работать!"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Не пустой пост",
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertNotEqual(
            Post.objects.count(), posts_count, "..а оно не работает!"
        )

    def test_post_edit_changes_post(self):
        """Проверка форм: редактирование должно изменять текст поста
         при сохранном id"""
        form_data = {
            "text": "Отредактированный текст",
        }
        self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            "Отредактированный текст",
            "Редактирование не работает",
        )
