import pytest
from django.urls import reverse


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


@pytest.mark.django_db
def test_course_creation(api_client_with_teacher_role):
    url = reverse('course-list')
    response = api_client_with_teacher_role.post(url, data={'name': 'Course',
                                                            'text': 'Text',
                                                            'categories': [],
                                                            })
    assert response.status_code == 201


@pytest.mark.django_db
def test_course_update(api_client_with_credentials_authentication, create_test_course, create_test_category):
    url = reverse('course-detail', kwargs={'pk': create_test_course.pk})
    api_client = api_client_with_credentials_authentication(create_test_course.author)
    response = api_client.patch(url, data={
        'categories': [
            {
                'category_id': create_test_category.pk
            }
        ]
    })
    assert response.status_code == 201


@pytest.mark.django_db
def test_course_detail(api_client, create_test_course):
    url = reverse('course-detail', kwargs={'pk': create_test_course.pk})
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_delete(api_client_with_credentials_authentication, create_test_course):
    url = reverse('course-detail', kwargs={'pk': create_test_course.pk})
    api_client = api_client_with_credentials_authentication(create_test_course.author)
    response = api_client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_course_list(api_client):
    url = reverse('course-list')
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
