import requests
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views.generic import FormView, View
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from .forms import AddCityForm

import API_KEYS
API_KEY = getattr(API_KEYS, 'WEATHER_MAP_API_KEY', None)


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
        return context

    def get_city_data(self, city):
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
        response = requests.get(url).json()

        if response.get('cod') != 200:
            return response
        return {
            'name': response['name'],
            'temperature': response['main']['temp'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
            'cod': response['cod']
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
