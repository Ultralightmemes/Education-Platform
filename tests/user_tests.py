import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_user_registration(api_client, test_email, test_password):
    url = reverse('user-registration')
    response = api_client.post(url, data={'email': test_email, 'password': test_password, 'last_name': 'last',
                                          'first_name': 'first'})
    assert response.status_code == 201


@pytest.mark.django_db
def test_user_info(api_client_with_credentials):
    url = reverse('user-info')
    response = api_client_with_credentials.get(url)
    assert response.status_code == 200
