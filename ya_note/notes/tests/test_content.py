from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    NOTE_LIST_URL = reverse('notes:list')
    number_of_records = 10

    @classmethod
    def setUpTestData(cls):
        all_notes = []
        cls.author = User.objects.create(username='Создатель Записи')
        for index in range(cls.number_of_records):
            note = Note(
                title=f'Запись {index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'slug_{index}'
            )
            all_notes.append(note)
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTE_LIST_URL)
        object_list = response.context['object_list']
        all_ids = [note.id for note in object_list]
        sorted_ids = sorted(all_ids)
        self.assertEqual(all_ids, sorted_ids)


class TestDetailPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Тестовая запись',
            text='Текст.',
            slug='slug',
            author=cls.author
        )
        cls.urls = (
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,))
        )

    def test_only_user_has_his_notes(self):
        self.another_user = User.objects.create(username='Another User')
        self.another_client = Client()
        self.another_client.force_login(self.another_user)

        self.new_note = Note.objects.create(
            title='New Тестовая запись',
            text='Текст.',
            slug='new_slug',
            author=self.author
        )

        url = reverse('notes:list')
        response = self.another_client.get(url)
        self.assertEqual(len(response.context['object_list']), 0)

        author_response = self.author_client.get(url)
        self.assertEqual(len(author_response.context['object_list']), 2)

    def test_authorized_client_has_form(self):
        for name, args in self.urls:
            url = reverse(name, args=args)
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
