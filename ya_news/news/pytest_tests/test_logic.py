from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


pytestmark = [pytest.mark.django_db]

COMMENT_TEXT = 'Текст комментария'
form_data = {'text': COMMENT_TEXT}
CREATED_COMMENTS = 1
DELETED_COMMENTS = 1


def test_anonymous_user_cant_create_comment(client, news):
    expectation_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comment_count = Comment.objects.count()
    assert comment_count == expectation_comments_count, (
        'Создание комментария анононимным пользователем проходит с ошибкой, '
        f'было комментариев: {expectation_comments_count}, '
        f'стало: {comment_count}, '
        f'ожидалось: {expectation_comments_count}'
    )


def test_user_can_create_comment(author, author_client, news):
    expectation_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count + CREATED_COMMENTS, (
        'Создание комментария проходит с ошибкой, '
        f'было комментариев: {expectation_comments_count}, '
        f'стало: {comments_count}, '
        f'ожидалось: {expectation_comments_count + CREATED_COMMENTS}'
    )
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_author_can_delete_comment(author_client, news, comment):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    url = reverse('news:delete', args=(comment.id,))
    expectation_comments_count = Comment.objects.count()
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count - DELETED_COMMENTS, (
        'Удаление комментария проходит с ошибкой, '
        f'было комментариев: {expectation_comments_count}, '
        f'стало: {comments_count}, '
        f'ожидалось: {expectation_comments_count - CREATED_COMMENTS}'
    )


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    comment_text_before = comment.text
    form_data['text'] = COMMENT_TEXT
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text_before, (
        'Редактирование комментария анонимным пользователем '
        f'проходит с ошибкой, изначальный текст: {comment_text_before}, '
        f'после изменений: {comment.text}, ожидалось: {comment_text_before}'
    )


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(author_client, news, bad_word):
    expectation_comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, ещё текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == expectation_comments_count, (
        'Создание комментария с неподобающим содержимым проходит с ошибкой, '
        f'было комментариев: {expectation_comments_count}, '
        f'стало: {comments_count}, '
        f'ожидалось: {expectation_comments_count}'
    )
