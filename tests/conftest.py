import uuid
from unittest.mock import MagicMock

import pytest
from django.core.files import File

from education.models import Course, Theme, Lesson, Category
from user.models import UserCourse


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def test_password():
    return 'strong-test-pass'


@pytest.fixture
def test_email():
    return str(uuid.uuid4().time_low) + '@gmail.com'


@pytest.fixture
def create_user(db, django_user_model, test_password, test_email):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'email' not in kwargs:
            kwargs['email'] = test_email
        kwargs['first_name'] = str(uuid.uuid4().time_low)
        kwargs['last_name'] = str(uuid.uuid4().time_low)
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def create_default_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'email' not in kwargs:
            kwargs['email'] = str(uuid.uuid4().time_low) + '@email.com'
        kwargs['first_name'] = str(uuid.uuid4().time_low)
        kwargs['last_name'] = str(uuid.uuid4().time_low)
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def api_client_with_teacher_role(db, create_user, api_client):
    user = create_user()
    user.is_teacher = True
    user.save()
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def api_client_with_credentials(db, create_user, api_client):
    user = create_user()
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def api_client_with_credentials_authentication(db, api_client):
    def wraps(user):
        api_client.force_authenticate(user=user)
        return api_client

    return wraps


@pytest.fixture
def create_mock_file():
    file_mock = MagicMock(spec=File)
    file_mock.name = 'Ruby.png'
    return file_mock


@pytest.fixture
def create_test_course(db, create_mock_file, create_default_user):
    user = create_default_user()
    user.is_teacher = True
    return Course.objects.create(name='Course',
                                 is_published=True,
                                 text='text',
                                 image=create_mock_file,
                                 author=user)


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


@pytest.fixture
def user_with_course_subscription(api_client_with_credentials_authentication, create_test_theme, create_default_user):
    user = create_default_user()
    UserCourse.objects.create(course_id=create_test_theme.course.id, user=user)
    return api_client_with_credentials_authentication(user), create_test_theme.course.id
