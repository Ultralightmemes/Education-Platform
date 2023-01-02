from unittest import mock

from django.core.files import File
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Course, Category
from education.serializers import CategorySerializer


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
        category_1 = Category(id=1, name='Python')
        category_2 = Category(id=2, name='Java')
        response = self.client.get(reverse('category-list'))
        serializer_data = CategorySerializer([category_1, category_2], many=True).data
        self.assertEqual(serializer_data, response.data)


class CoursesTest(APITestCase):
    def setUp(self):
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = 'Ruby.png'
        Course.objects.create(name='Python', is_published=True, text='text', image=file_mock)
        Course.objects.create(name='Java', is_published=False, text='text', image=file_mock)

    def test_course_detail(self):
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('name'), 'Python')

    def test_course_list(self):
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
