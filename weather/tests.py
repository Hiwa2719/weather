import time

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse, HttpResponseRedirect
from django.test import TestCase, RequestFactory
from django.template.response import TemplateResponse
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .forms import AddCityForm
from .views import IndexView


class FunctionalTestCase(TestCase):
    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, 15)

    def test_get_index(self):
        self.browser.get('http://127.0.0.1:8000/')
        self.assertIn("What's the weather like?", self.browser.page_source)

    def add_city(self, city, timer=5):
        self.browser.get('http://127.0.0.1:8000/')
        form = self.browser.find_element_by_id('id_city')
        form.send_keys(city)
        self.browser.find_element_by_id('form-button').click()

    def test_post_index(self):
        self.add_city('marivan')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card-detail')))
        self.assertIn('Marivan', self.browser.page_source)

    def test_post_index_wrong_city(self):
        self.add_city('sna', 15)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'form-errors')))
        self.assertIn('City Not Found', self.browser.page_source)

    def test_remove_city(self):
        self.add_city('marivan')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'close')))
        self.browser.find_element_by_class_name('close').click()
        self.wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, 'card-detail')))
        self.assertNotIn('Marivan', self.browser.page_source)

    def test_new_list(self):
        self.add_city('marivan')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card-detail')))
        self.browser.find_element_by_id('new-list').click()
        self.assertNotIn('Marivan', self.browser.page_source)

    def test_repetitive_city(self):
        self.add_city('marivan')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card-detail')))
        self.add_city('marivan')
        self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'form-errors')))
        self.assertIn('This City Already Exists In List', self.browser.page_source)

    def tearDown(self) -> None:
        self.browser.quit()


class IndexViewTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def setup_view(self, request):
        view = IndexView()
        view.setup(request)
        return view

    def test_context_data_empty_session(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = SessionStore()
        view = self.setup_view(request)
        context = view.get_context_data()
        self.assertIn('cities', context)
        self.assertEqual(context['cities'], [])
        self.assertIn('days', context)
        self.assertEqual(context['days'], range(7))

    def test_context_data_with_city_in_session(self):
        request = self.factory.get('/')
        session = SessionStore()
        session['city_Marivan'] = 'Marivan'
        request.session = session
        view = self.setup_view(request)
        context = view.get_context_data()
        self.assertEqual(context['cities'][0]['name'], 'Marivan')
        self.assertEqual(context['days'], range(7))
        # correct city name
        city_data = view.get_city_data('Marivan')
        self.assertEqual(city_data['cod'], 200)
        # Wrong city name
        city_data = view.get_city_data('sna')
        self.assertNotEqual(city_data['cod'], 200)

    def test_form_valid(self):
        request = self.factory.post('/', data={'city': 'marivan'})
        request.session = SessionStore()
        view = self.setup_view(request)
        form = AddCityForm(data={'city': 'marivan'})
        form.is_valid()
        form_valid_method = view.form_valid(form)
        from django.http import HttpResponseRedirect
        self.assertEqual(form_valid_method.__class__, HttpResponseRedirect)
        self.assertEqual(form_valid_method.status_code, 302)
        self.assertEqual(form_valid_method.url, reverse('weather:index'))

    def test_form_valid_ajax(self):
        request = self.factory.post('/', data={'city': 'marivan'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.session = SessionStore()
        view = self.setup_view(request)
        form = AddCityForm(data={'city': 'marivan'})
        form.is_valid()
        form_valid_method = view.form_valid(form)
        self.assertEqual(form_valid_method.__class__, JsonResponse)
        self.assertEqual(form_valid_method.status_code, 200)

    def test_form_invalid(self):
        request = self.factory.post('/', {'city': 'sna'})
        request.session = SessionStore()
        view = self.setup_view(request)
        form_invalid_method = view.form_invalid(
            AddCityForm({'city': 'sna'}),
            'wrong message'
        )
        self.assertEqual(form_invalid_method.status_code, 200)
        self.assertEqual(form_invalid_method.__class__, TemplateResponse)

    def test_form_invalid_ajax(self):
        request = self.factory.post('/', {'city': 'sna'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        view = self.setup_view(request)
        form_invalid_method = view.form_invalid(
            {},
            'Wrong message'
        )
        self.assertEqual(form_invalid_method.status_code, 403)
        self.assertJSONEqual(str(form_invalid_method.content, encoding='utf-8'),
                             {'errorMessage': 'Wrong message'.title()})

    def test_index_view_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('weather/index.html')
        self.assertIn('cities', response.context)
        self.assertIn('days', response.context)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertEqual(form.__class__, AddCityForm)

    def test_index_view_post(self):
        response = self.client.post('/', data={'city': 'marivan'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['city_Marivan'], 'Marivan')


class NewListTest(TestCase):

    def test_new_list(self):
        session = self.client.session
        session['city_marivan'] = 'marivan'
        session.save()
        response = self.client.get(reverse('weather:new_list'), follow=True)
        print(response.request.get('PATH_INFO'))
        self.assertNotEqual(self.client.session.get('city_marivan'), 'marivan')


class RemoveCityTest(TestCase):
    def test_remove_city(self):
        session = self.client.session
        session['city_marivan'] = 'marivan'
        session.save()
        self.client.post(reverse('weather:remove_city'), data={'city-name': 'marivan'})
        self.assertNotEqual(self.client.session.get('city_marivan'), 'marivan')

    def test_remove_without_city(self):
        response = self.client.post(reverse('weather:remove_city'), {'city-name': 'marivan'})
        self.assertEqual(response.status_code, 200)


class GetModalDetailTest(TestCase):
    def test_get_modal_detail(self):
        response = self.client.post(reverse('weather:modal-detail'),
                                    data={'city-name': 'marivan', 'lat': 35.5219, 'lon': 46.176})
        self.assertEqual(response.status_code, 200)

    def test_get_modal_detail_wrong_data(self):
        response = self.client.post(reverse('weather:modal-detail'),
                                    data={'city-name': 'mariva', 'lat': '', 'lon': ''})
        self.assertEqual(response.status_code, 403)
