import pytz
import random
import requests
from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views.generic import FormView, View
from tzwhere import tzwhere

import API_KEYS
from .forms import AddCityForm

WEATHER_MAP_API_KEY = getattr(API_KEYS, 'WEATHER_MAP_API_KEY')
PEXEL_API_KEY = getattr(API_KEYS, 'PEXEL_API_KEY')
tz = tzwhere.tzwhere()


class GetModalDetail(View):
    def post(self, request, *args, **kwargs):
        """for capturing 7 days data"""
        city = request.POST.get("city-name")
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}" \
              f"&units=metric&exclude=current,minutely,hourly,alerts&appid={WEATHER_MAP_API_KEY}"
        response = requests.get(url).json()
        if response.get('cod') == '400':
            return JsonResponse({'msg': 'wrong location'}, status=403)
        days = []
        for item in response['daily']:
            date_time = datetime.fromtimestamp(item['dt'])
            days.append({
                'date': date_time.strftime('%a %d'),
                'date2': date_time.strftime('%d/%m/%Y'),
                'min': item['temp']['min'],
                'max': item['temp']['max'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon'],
            })
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={WEATHER_MAP_API_KEY}'
        response = requests.get(url).json()
        if response.get('cod') == '400':
            return JsonResponse({'msg': 'wrong location'}, status=403)
        hours = []
        for d in response['list']:
            date_time = datetime.utcfromtimestamp(d['dt'])
            hours.append({
                'date': date_time.strftime('%d/%m/%Y'),
                'time': date_time.strftime('%I %p'),
                'temp': d['main']['temp'],
                'wind': d['wind'],
                'description': d['weather'][0]['description'],
                'icon': d['weather'][0]['icon']
            })
        template = get_template('weather/modal.html')
        modal_render = template.render({'days': days, 'hours': hours, 'city_name': city})
        return JsonResponse({'modalRender': modal_render})


class IndexView(FormView):
    template_name = 'weather/index.html'
    form_class = AddCityForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.request.session
        cities_list = [session[key] for key in session.keys() if key.startswith('city_')]
        searched_list = []
        for city in cities_list:
            searched_list.append(self.get_city_data(city))
        context['cities'] = searched_list
        context['days'] = range(7)
        context['background_image'] = self.get_photo_url()
        return context

    @staticmethod
    def get_photo_url():
        """Gets a photo url from pexels.com"""
        url = "https://api.pexels.com/v1/search?query=landscape&orientation=landscape" \
              f"&Authorization={PEXEL_API_KEY}&size=large&per_page=80"
        response = requests.get(url,
                                headers={
                                    'authorization': PEXEL_API_KEY
                                }).json()
        photo_dict = random.choice(response['photos'])
        return photo_dict['src']['original']

    @staticmethod
    def get_city_data(city):
        """Catches data per city from OpenWeatherMap"""
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={WEATHER_MAP_API_KEY}'
        response = requests.get(url).json()
        if response.get('cod') != 200:

            return response
        lat = response['coord']['lat']
        lon = response['coord']['lon']
        tz_string = tz.tzNameAt(lat, lon)
        timezone = pytz.timezone(tz_string)
        return {
            'name': response['name'],
            'temperature': response['main']['temp'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
            'cod': response['cod'],
            'lat': lat,
            'lon': lon,
            'local_time': datetime.now(tz=timezone).time(),
        }

    def form_valid(self, form):
        city = form.cleaned_data.get('city').lower()
        session = self.request.session
        if len([key for key in session.keys() if key.startswith('city_')]) == 9:
            return self.form_invalid(form, "Sorry you can not add more than nine cities")
        response = self.get_city_data(city)
        if response.get('cod') != 200:
            return self.form_invalid(form, response['message'])
        city_name = response['name']
        session_key = 'city_{}'.format(city_name)
        if session.get(session_key):
            return self.form_invalid(form, 'This city already exists in list')
        session[session_key] = city_name
        template = get_template('weather/city_card.html')
        new_city = template.render({'city': response}, request=self.request)
        if self.request.is_ajax():
            return JsonResponse({'new_city': new_city})
        return redirect('weather:index')

    # @method_decorator(vary_on_headers('X-Requested-With'))
    def form_invalid(self, form, message):
        if self.request.is_ajax():
            return JsonResponse({'errorMessage': message.title()}, status=403)
        return super().form_invalid(form)


class NewList(View):
    """this view gives an new page by flushing session"""
    def get(self, request, *args, **kwargs):
        request.session.flush()
        return redirect('weather:index')


class RemoveCity(View):
    """This view removes a city from page"""
    def post(self, request, *args, **kwargs):
        city = request.POST.get('city-name')
        session_key = f'city_{city}'
        try:
            del request.session[session_key]
        except KeyError:
            pass
        return JsonResponse({})
