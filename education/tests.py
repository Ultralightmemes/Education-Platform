from unittest import mock

from django.core.files import File
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Course, Category, Theme, Lesson
from education.serializers import CategorySerializer
from user.models import User


class CategoriesTest(APITestCase):
    def setUp(self):
        Category.objects.create(name='Python')
        Category.objects.create(name='Java')

    def test_categories_list(self):
        response = self.client.get(reverse('category-list'))
        self.assertTrue({'id': 1, 'name': 'Python'} in response.data)

    def test_category_detail(self):
        response = self.client.get(reverse('category-detail', kwargs={'pk': 10}))
        self.assertEqual(response.data, [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_serializer(self):
        category_1 = Category(id=5, name='Python')
        category_2 = Category(id=6, name='Java')
        response = self.client.get(reverse('category-list'))
        serializer_data = CategorySerializer([category_1, category_2], many=True).data
        self.assertEqual(serializer_data, response.data)


class CoursesTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@gmail.com', password='123', first_name='name',
                                             last_name='last name')
        self.client.force_authenticate(self.user)
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = 'Ruby.png'
        course_1 = Course.objects.create(name='Python', is_published=True, text='text', image=file_mock)
        course_2 = Course.objects.create(name='Java', is_published=False, text='text', image=file_mock)
        theme_1 = Theme.objects.create(title='Core', course=course_1, position=1, description='Description',
                                       is_published=True)
        Theme.objects.create(title='OOP', course=course_1, position=2, description='Description 2', is_published=False)
        Theme.objects.create(title='WEB', course=course_1, position=3, description='Description 3', is_published=True)
        Theme.objects.create(title='Core', course=course_2, position=1, description='Description 1', is_published=True)
        Lesson.objects.create(title='First', theme=theme_1, position=1, text='text', is_published=True)
        Lesson.objects.create(title='Second', theme=theme_1, position=2, text='text', is_published=False)

    def test_A_course_detail(self):
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('name'), 'Python')

    def test_B_course_list(self):
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_C_themes_with_lessons(self):
        response = self.client.get(reverse('course-get-themes-with-lessons', kwargs={'pk': 5}))
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(len(response.json()[0].get('lessons')), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_D_follow_course(self):
        response = self.client.post(reverse('course-follow-course', kwargs={'pk': 7}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.user.courses.all()), 1)

    def test_E_user_courses(self):
        self.client.post(reverse('course-follow-course', kwargs={'pk': 9}))
        response = self.client.get(reverse('course-get-user-courses'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_F_lesson_list(self):
        response = self.client.get(reverse('course-lesson-list', kwargs={'course_pk': 11}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('title'), 'First')
