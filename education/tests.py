# import pytest
# from django.urls import reverse
#
#
# @pytest.fixture
# def api_client_with_credentials(db, create_user, api_client):
#     user = create_user()
#     api_client.force_authenticate(user=user)
#     yield api_client
#     api_client.force_authenticate(user=None)
#
#
# @pytest.mark.django_db
# def test_authorized_request(api_client_with_credentials):
#     url = reverse('course-get-user-courses')
#     response = api_client_with_credentials.get(url)
#     assert response.status_code == 200
