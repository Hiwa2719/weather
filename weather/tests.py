from selenium import webdriver
from django.test import TestCase

from .forms import AddCityForm


class UnitTestCase(TestCase):

    def setUp(self) -> None:
        pass

    def test_index_view_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('weather/weather.html')
        self.assertIn('cities', response.context)
        self.assertIn('days', response.context)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertEqual(form.__class__, AddCityForm)

    def test_index_view_post(self):
        response = self.client.post('/', data={'city': 'marivan'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['city_Marivan'], 'Marivan')

