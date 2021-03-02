import requests
import json
from datetime import datetime, date
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views.generic import FormView, View

from .forms import AddCityForm

import API_KEYS
API_KEY = getattr(API_KEYS, 'WEATHER_MAP_API_KEY', None)


class GetModalDetail(View):
    def post(self, request, *args, **kwargs):
        """for capturing 7 days data"""
        city = request.POST.get("city-name")
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=metric&exclude=current,minutely,hourly,alerts&appid={API_KEY}'
        response = requests.get(url).json()
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
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={API_KEY}'
        response = requests.get(url).json()
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
    template_name = 'weather/weather.html'
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
        context['escaped'] = '<p class="bold">escaped</p>',
        return context

    @staticmethod
    def get_city_data(city):
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
        response = requests.get(url).json()

        if response.get('cod') != 200:
            return response
        return {
            'name': response['name'],
            'temperature': response['main']['temp'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
            'cod': response['cod'],
            'lat': response['coord']['lat'],
            'lon': response['coord']['lon'],
        }

    def form_valid(self, form):
        city = form.cleaned_data.get('city').lower()
        session = self.request.session
        response = self.get_city_data(city)
        if response.get('cod') != 200:
            return self.form_invalid(form, response['message'])
        city_name = response['name']
        session_key = 'city_{}'.format(city_name)
        if session.get(session_key):
            return self.form_invalid(form, 'This city already exists in list')
        session[session_key] = response['name']
        template = get_template('weather/city_card.html')
        new_city = template.render({'cities': [response]}, request=self.request)
        if self.request.is_ajax():
            return JsonResponse({'new_city': new_city})
        return redirect('weather:index')

    # @method_decorator(vary_on_headers('X-Requested-With'))
    def form_invalid(self, form, message):
        if self.request.is_ajax():
            return JsonResponse({'errorMessage': message.title()}, status=403)
        return super().form_invalid(form)


class NewList(View):
    def get(self, request, *args, **kwargs):
        request.session.flush()
        return redirect('weather:index')


class RemoveCity(View):
    def post(self, request, *args, **kwargs):
        city = request.POST.get('city-name')
        session_key = f'city_{city}'
        del request.session[session_key]
        return JsonResponse({})
