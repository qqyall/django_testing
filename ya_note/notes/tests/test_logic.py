from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()
NOTES_CREATED = 1


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Note title'
    NOTE_TEXT = 'Note text'
    NOTE_SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Cool User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse(
            'notes:add'
        )
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }
        cls.success_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        expectation_notes_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, expectation_notes_count)

    def test_user_can_create_note(self):
        expectation_notes_count = Note.objects.count()
        response = self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, expectation_notes_count + NOTES_CREATED)
        self.assertRedirects(response, self.success_url)

        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_cant_create_note_with_not_unique_slug(self):
        new_form_data = {
            'title': f'New {self.NOTE_TITLE}',
            'text': f'New {self.NOTE_TEXT}',
            'slug': self.NOTE_SLUG,
        }

        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.auth_client.post(self.url, data=new_form_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Note title'
    NOTE_TEXT = 'Note text'
    NOTE_SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Cool User')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='NotSoCool User')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': f'new {cls.NOTE_TITLE}',
            'text': f'new {cls.NOTE_TEXT}',
            'slug': f'new_{cls.NOTE_SLUG}',
            'author': cls.author
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()

        self.assertEqual(self.note.title, f'new {self.NOTE_TITLE}')
        self.assertEqual(self.note.text, f'new {self.NOTE_TEXT}')
        self.assertEqual(self.note.slug, f'new_{self.NOTE_SLUG}')

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()

        self.assertEqual(self.note.title, f'{self.NOTE_TITLE}')
        self.assertEqual(self.note.text, f'{self.NOTE_TEXT}')
        self.assertEqual(self.note.slug, f'{self.NOTE_SLUG}')
