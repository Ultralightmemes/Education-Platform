import pytest
from django.urls import reverse


def test_course_detail(api_client_with_credentials_authentication, create_test_course):
    url = reverse('teacher-course-detail', kwargs={'pk': create_test_course.pk})
    api_client = api_client_with_credentials_authentication(create_test_course.author)
    response = api_client.get(url)
    assert response.status_code == 200


def test_course_list(api_client_with_credentials_authentication, create_test_course):
    url = reverse('teacher-course')
    api_client = api_client_with_credentials_authentication(create_test_course.author)
    response = api_client.get(url)
    assert response.status_code == 200


def test_course_creation(api_client_with_teacher_role):
    url = reverse('teacher-course')
    response = api_client_with_teacher_role.post(url, data={'name': 'Course',
                                                            'text': 'Text',
                                                            'categories': [],
                                                            })
    assert response.status_code == 201


def test_course_delete(api_client_with_credentials_authentication, create_test_course):
    url = reverse('teacher-course-detail', kwargs={'pk': create_test_course.pk})
    api_client = api_client_with_credentials_authentication(create_test_course.author)
    response = api_client.delete(url)
    assert response.status_code == 204


def test_course_update(api_client_with_credentials_authentication, create_test_course, create_test_category):
    url = reverse('teacher-course-detail', kwargs={'pk': create_test_course.pk})
    api_client = api_client_with_credentials_authentication(create_test_course.author)
    response = api_client.patch(url, data={'text': 'text',
                                           'categories': [
                                               {
                                                   'category_id': create_test_category.pk
                                               }
                                           ]})
    assert response.status_code == 200


@pytest.mark.django_db
def test_theme_detail(api_client_with_credentials_authentication, create_test_theme):
    url = reverse('teacher-theme-detail', kwargs={'pk': create_test_theme.pk})
    api_client = api_client_with_credentials_authentication(create_test_theme.course.author)
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_theme_update(api_client_with_credentials_authentication, create_test_theme):
    url = reverse('teacher-theme-detail', kwargs={'pk': create_test_theme.pk})
    api_client = api_client_with_credentials_authentication(create_test_theme.course.author)
    response = api_client.patch(url, data={'title': 'title'})
    assert response.status_code == 200


@pytest.mark.django_db
def test_theme_delete(api_client_with_credentials_authentication, create_test_theme):
    url = reverse('teacher-theme-detail', kwargs={'pk': create_test_theme.pk})
    api_client = api_client_with_credentials_authentication(create_test_theme.course.author)
    print(create_test_theme.course.author)
    response = api_client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_authorized_themes_with_lessons(api_client_with_credentials_authentication, create_test_lesson):
    url = reverse('teacher-theme-list', kwargs={'course_pk': create_test_lesson.theme.course.pk})
    api_client = api_client_with_credentials_authentication(create_test_lesson.theme.course.author)
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthorized_themes_with_lessons(api_client, create_test_lesson):
    url = reverse('teacher-theme-list', kwargs={'course_pk': create_test_lesson.theme.course.pk})
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_theme_creation(api_client_with_credentials_authentication, create_test_course):
    url = reverse('teacher-theme-list', kwargs={'course_pk': create_test_course.pk})
    api_client = api_client_with_credentials_authentication(create_test_course.author)
    response = api_client.post(url, data={'title': 'test',
                                          'description': 'desc',
                                          'is_published': True,
                                          'position': 1,
                                          'course': create_test_course.pk})
    assert response.status_code == 201