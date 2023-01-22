from unittest.mock import MagicMock

import pytest
from django.core.files import File
from django.urls import reverse

from education.models import Course, Theme, Lesson, Category
from user.models import UserCourse


@pytest.mark.django_db
def test_authorized_user_courses(api_client_with_credentials):
    url = reverse('course-get-user-courses')
    response = api_client_with_credentials.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_list(api_client):
    url = reverse('course-list')
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.fixture
def create_mock_file():
    file_mock = MagicMock(spec=File)
    file_mock.name = 'Ruby.png'
    return file_mock


@pytest.fixture
def create_test_course(db, create_mock_file, create_default_user):
    return Course.objects.create(name='Course',
                                 is_published=True,
                                 text='text',
                                 image=create_mock_file,
                                 author=create_default_user())


@pytest.fixture
def create_test_theme(db, create_test_course):
    return Theme.objects.create(title='Title',
                                course=create_test_course,
                                description='description',
                                is_published=True,
                                position=1)


@pytest.fixture
def create_test_lesson(db, create_test_theme):
    return Lesson.objects.create(title='Lesson',
                                 theme=create_test_theme,
                                 text='text',
                                 is_published=True,
                                 position=1)


@pytest.fixture
def create_test_category(db, create_test_course):
    category = Category.objects.create(name='Category')
    category.courses.add(create_test_course)
    category.save()
    return category


@pytest.fixture
def create_user_subscription_to_course(db, create_user, create_test_course):
    return UserCourse.objects.create(user=create_user(), course=create_test_course)


@pytest.mark.django_db
def test_course_creation(api_client_with_teacher_role):
    url = reverse('course-list')
    response = api_client_with_teacher_role.post(url, data={'name': 'Course', 'text': 'Text'})
    assert response.status_code == 201


@pytest.mark.django_db
def test_course_detail(api_client, create_test_course):
    url = reverse('course-detail', kwargs={'pk': create_test_course.pk})
    response = api_client.get(url)
    assert response.status_code == 200


# @pytest.mark.django_db
# def test_user_subscribe(api_client_with_credentials, create_test_course, redis_proc):
#     url = reverse('course-follow-course', kwargs={'pk': create_test_course.pk})
#     response = api_client_with_credentials.post(url)
#     assert response.status_code == 200


@pytest.mark.django_db
def test_rate_course(create_user_subscription_to_course, api_client):
    url = reverse('course-rate', kwargs={'pk': create_user_subscription_to_course.course.pk})
    api_client.force_authenticate(create_user_subscription_to_course.user)
    response = api_client.post(url, data={'rating': 5})
    assert response.status_code == 201


@pytest.mark.django_db
def test_category_list(create_test_category, api_client):
    url = reverse('category-list')
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_category_detail(create_test_category, api_client):
    url = reverse('category-detail', kwargs={'pk': create_test_category.pk})
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_lesson_list(api_client_with_credentials, create_test_lesson):
    url = reverse('course-lesson-list', kwargs={'course_pk': create_test_lesson.theme.course.pk})
    response = api_client_with_credentials.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_lesson_detail(api_client_with_credentials, create_test_lesson):
    url = reverse('course-lesson-detail',
                  kwargs={'pk': create_test_lesson.pk, 'course_pk': create_test_lesson.theme.course.pk})
    response = api_client_with_credentials.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_lesson_answer(api_client_with_credentials, create_test_lesson):
    url = reverse('course-lesson-answer',
                  kwargs={'pk': create_test_lesson.pk, 'course_pk': create_test_lesson.theme.course.pk})
    response = api_client_with_credentials.post(url)
    assert response.status_code == 202


@pytest.mark.django_db
def test_authorized_themes_with_lessons(api_client_with_credentials, create_test_lesson):
    url = reverse('theme-list')
    response = api_client_with_credentials.get(url, data={'course': create_test_lesson.theme.course.pk})
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthorized_themes_with_lessons(api_client, create_test_lesson):
    url = reverse('theme-list')
    response = api_client.get(url, data={'course': create_test_lesson.theme.course.pk})
    assert response.status_code == 401


# @pytest.mark.django_db
# def test_theme_creation(api_client_with_credentials_authentication, create_test_course):
#     url = reverse('theme-list')

