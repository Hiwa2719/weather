from django import forms


class AddCityForm(forms.Form):
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
