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
from unittest import mock

import API_KEYS
from .forms import AddCityForm
from .views import IndexView

WEATHER_MAP_API_KEY = getattr(API_KEYS, 'WEATHER_MAP_API_KEY')
PEXEL_API_KEY = getattr(API_KEYS, 'PEXEL_API_KEY')


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
        self.assertNotIn('marivan', self.browser.page_source)

    def test_new_list(self):
        self.add_city('marivan')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card-detail')))
        self.browser.find_element_by_id('new-list').click()
        self.assertNotIn('marivan', self.browser.page_source)

    def test_repetitive_city(self):
        self.add_city('marivan')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card-detail')))
        self.add_city('marivan')
        self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'form-errors')))
        self.assertIn('This City Already Exists In List', self.browser.page_source)

    def tearDown(self) -> None:
        self.browser.quit()


def add_city_to_session(client, city='marivan'):
    session = client.session
    session[f'city_{city}'] = city


city_response = {
    "coord": {
        "lon": -122.08,
        "lat": 37.39
    },
    "weather": [
        {
            "id": 800,
            "main": "Clear",
            "description": "clear sky",
            "icon": "01d"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 282.55,
        "feels_like": 281.86,
        "temp_min": 280.37,
        "temp_max": 284.26,
        "pressure": 1023,
        "humidity": 100
    },
    "visibility": 16093,
    "wind": {
        "speed": 1.5,
        "deg": 350
    },
    "clouds": {
        "all": 1
    },
    "dt": 1560350645,
    "sys": {
        "type": 1,
        "id": 5122,
        "message": 0.0139,
        "country": "US",
        "sunrise": 1560343627,
        "sunset": 1560396563
    },
    "timezone": -25200,
    "id": 420006353,
    "name": "marivan",
    "cod": 200
}
lat_lon_response = {
    "lat": 33.44,
    "lon": -94.04,
    "timezone": "America/Chicago",
    "timezone_offset": -21600,
    "current": {
        "dt": 1618317040,
        "sunrise": 1618282134,
        "sunset": 1618333901,
        "temp": 284.07,
        "feels_like": 282.84,
        "pressure": 1019,
        "humidity": 62,
        "dew_point": 277.08,
        "uvi": 0.89,
        "clouds": 0,
        "visibility": 10000,
        "wind_speed": 6,
        "wind_deg": 300,
        "weather": [
            {
                "id": 500,
                "main": "Rain",
                "description": "light rain",
                "icon": "10d"
            }
        ],
        "rain": {
            "1h": 0.21
        }
    },
    "minutely": [
        {
            "dt": 1618317060,
            "precipitation": 0.205
        }],
    "hourly": [
        {
            "dt": 1618315200,
            "temp": 282.58,
            "feels_like": 280.4,
            "pressure": 1019,
            "humidity": 68,
            "dew_point": 276.98,
            "uvi": 1.4,
            "clouds": 19,
            "visibility": 306,
            "wind_speed": 4.12,
            "wind_deg": 296,
            "wind_gust": 7.33,
            "weather": [
                {
                    "id": 801,
                    "main": "Clouds",
                    "description": "few clouds",
                    "icon": "02d"
                }
            ],
            "pop": 0
        }
    ],
    "daily": [
        {
            "dt": 1618308000,
            "sunrise": 1618282134,
            "sunset": 1618333901,
            "moonrise": 1618284960,
            "moonset": 1618339740,
            "moon_phase": 0.04,
            "temp": {
                "day": 279.79,
                "min": 275.09,
                "max": 284.07,
                "night": 275.09,
                "eve": 279.21,
                "morn": 278.49
            },
            "feels_like": {
                "day": 277.59,
                "night": 276.27,
                "eve": 276.49,
                "morn": 276.27
            },
            "pressure": 1020,
            "humidity": 81,
            "dew_point": 276.77,
            "wind_speed": 3.06,
            "wind_deg": 294,
            "weather": [
                {
                    "id": 500,
                    "main": "Rain",
                    "description": "light rain",
                    "icon": "10d"
                }
            ],
            "clouds": 56,
            "pop": 0.2,
            "rain": 0.62,
            "uvi": 1.93
        }]
}
days_hours_response = {
  "cod": "200",
  "message": 0,
  "cnt": 40,
  "list": [
    {
      "dt": 1596564000,
      "main": {
        "temp": 293.55,
        "feels_like": 293.13,
        "temp_min": 293.55,
        "temp_max": 294.05,
        "pressure": 1013,
        "sea_level": 1013,
        "grnd_level": 976,
        "humidity": 84,
        "temp_kf": -0.5
      },
      "weather": [
        {
          "id": 500,
          "main": "Rain",
          "description": "light rain",
          "icon": "10d"
        }
      ],
      "clouds": {
        "all": 38
      },
      "wind": {
        "speed": 4.35,
        "deg": 309,
        "gust": 7.87
      },
      "visibility": 10000,
      "pop": 0.49,
      "rain": {
        "3h": 0.53
      },
      "sys": {
        "pod": "d"
      },
      "dt_txt": "2020-08-04 18:00:00"
    },
],
"city": {
    "id": 2643743,
    "name": "London",
    "coord": {
      "lat": 51.5073,
      "lon": -0.1277
    },
    "country": "GB",
    "timezone": 0,
    "sunrise": 1578384285,
    "sunset": 1578413272
  }
}


def requests_mock_side_effect(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

    # IndexView
    url = f'http://api.openweathermap.org/data/2.5/weather?q=marivan&units=metric&appid={WEATHER_MAP_API_KEY}'
    if args[0] == url:
        return MockResponse(city_response)
    url = "https://api.pexels.com/v1/search?query=landscape&orientation=landscape" \
                  f"&Authorization={PEXEL_API_KEY}&size=large&per_page=80"
    if args[0] == url:
        return MockResponse({'photos': [{'src': {'original': 'original'}}]})
    url = f'http://api.openweathermap.org/data/2.5/weather?q=asdf&units=metric&appid={WEATHER_MAP_API_KEY}'
    if args[0] == url:
        return MockResponse({'cod': '400'})

    # test_get_modal_detail
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat=35.5219&lon=46.176" \
          f"&units=metric&exclude=current,minutely,hourly,alerts&appid={WEATHER_MAP_API_KEY}"
    if args[0] == url:
        return MockResponse(lat_lon_response)
    url = f'http://api.openweathermap.org/data/2.5/forecast?q=marivan&units=metric&appid={WEATHER_MAP_API_KEY}'
    if args[0] == url:
        return MockResponse(days_hours_response)
    # test_get_modal_detail_wrong_data
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat=&lon=" \
          f"&units=metric&exclude=current,minutely,hourly,alerts&appid={WEATHER_MAP_API_KEY}"
    if args[0] == url:
        return MockResponse({'cod': '400'})
    url = f'http://api.openweathermap.org/data/2.5/forecast?q=asdf&units=metric&appid={WEATHER_MAP_API_KEY}'
    if args[0] == url:
        return MockResponse({'cod': '400'})


@mock.patch('weather.views.requests.get', side_effect=requests_mock_side_effect)
class IndexViewTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def setup_view(self, request):
        view = IndexView()
        view.setup(request)
        return view

    def test_context_data_empty_session(self, mock_obj):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = SessionStore()
        view = self.setup_view(request)
        context = view.get_context_data()
        self.assertIn('cities', context)
        self.assertEqual(context['cities'], [])
        self.assertIn('days', context)
        self.assertEqual(context['days'], range(7))

    def test_context_data_with_city_in_session(self, mock_obj):
        request = self.factory.get('/')
        session = SessionStore()
        session['city_marivan'] = 'marivan'
        request.session = session
        view = self.setup_view(request)
        context = view.get_context_data()
        self.assertEqual(context['cities'][0]['name'], 'marivan')
        self.assertEqual(context['days'], range(7))
        # correct city name
        city_data = view.get_city_data('marivan')
        self.assertEqual(city_data['cod'], 200)
        # Wrong city name
        city_data = view.get_city_data('asdf')
        self.assertNotEqual(city_data['cod'], 200)

    def test_form_valid(self, mock_obj):
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

    def test_form_valid_ajax(self, mock_obj):
        request = self.factory.post('/', data={'city': 'marivan'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.session = SessionStore()
        view = self.setup_view(request)
        form = AddCityForm(data={'city': 'marivan'})
        form.is_valid()
        form_valid_method = view.form_valid(form)
        self.assertEqual(form_valid_method.__class__, JsonResponse)
        self.assertEqual(form_valid_method.status_code, 200)

    def test_form_invalid(self, mock_obj):
        request = self.factory.post('/', {'city': 'sna'})
        request.session = SessionStore()
        view = self.setup_view(request)
        form_invalid_method = view.form_invalid(
            AddCityForm({'city': 'sna'}),
            'wrong message'
        )
        self.assertEqual(form_invalid_method.status_code, 200)
        self.assertEqual(form_invalid_method.__class__, TemplateResponse)

    def test_form_invalid_ajax(self, mock_obj):
        request = self.factory.post('/', {'city': 'sna'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        view = self.setup_view(request)
        form_invalid_method = view.form_invalid(
            {},
            'Wrong message'
        )
        self.assertEqual(form_invalid_method.status_code, 403)
        self.assertJSONEqual(str(form_invalid_method.content, encoding='utf-8'),
                             {'errorMessage': 'Wrong message'.title()})

    def test_index_view_get(self, mock_obj):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('weather/index.html')
        self.assertIn('cities', response.context)
        self.assertIn('days', response.context)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertEqual(form.__class__, AddCityForm)

    def test_index_view_post(self, mock_obj):
        response = self.client.post('/', data={'city': 'marivan'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['city_marivan'], 'marivan')


class NewListTest(TestCase):
    def test_new_list(self):
        add_city_to_session(self.client)
        response = self.client.get(reverse('weather:new_list'), follow=True)
        self.assertNotEqual(self.client.session.get('city_marivan'), 'marivan')


class RemoveCityTest(TestCase):
    def test_remove_city(self):
        add_city_to_session(self.client)
        self.client.post(reverse('weather:remove_city'), data={'city-name': 'marivan'})
        self.assertNotEqual(self.client.session.get('city_marivan'), 'marivan')

    def test_remove_without_city(self):
        response = self.client.post(reverse('weather:remove_city'), {'city-name': 'marivan'})
        self.assertEqual(response.status_code, 200)


@mock.patch('weather.views.requests.get', side_effect=requests_mock_side_effect)
class GetModalDetailTest(TestCase):
    def test_get_modal_detail(self, mock_obj):
        response = self.client.post(reverse('weather:modal-detail'),
                                    data={'city-name': 'marivan', 'lat': 35.5219, 'lon': 46.176})
        self.assertEqual(response.status_code, 200)

    def test_get_modal_detail_wrong_data(self, mock_obj):
        response = self.client.post(reverse('weather:modal-detail'),
                                    data={'city-name': 'asdf', 'lat': '', 'lon': ''})
        self.assertEqual(response.status_code, 403)
