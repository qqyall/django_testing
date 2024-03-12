from http import HTTPStatus

import pytest
from django.urls import reverse

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_page_detail_availability_for_anonymous_user(client, news):
    name = 'news:detail'
    url = reverse(name, args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(client, name, comment):
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_comment_edit_delete_pages_for_comment_author(author_client,
                                                      comment, name):
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_comment_edit_delete_pages_for_not_comment_author(not_author_client,
                                                          comment, name):
    url = reverse(name, args=(comment.id,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
