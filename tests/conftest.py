import uuid

import pytest


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
            kwargs['email'] = 'test_email@email.com'
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


# @pytest.fixture
# def api_client_with_credentials_authentication(db, api_client, user):
#     api_client.force_authenticate(user=user)
#     yield api_client
#     api_client.force_authenticate(user=None)
