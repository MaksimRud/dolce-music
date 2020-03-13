from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm
from .validators import *
from .models import *


class PeriodForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', }), validators=[RegexValidator(regex='^\w+$')])
    time_of_period = forms.CharField(validators=[RegexValidator(
        regex='^[1-9]([0-9]{3})[-][1-9]([0-9]{3})$', message='invalid time period', code='invalid_period'), validate_year], widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Period
        fields = '__all__'

    def clean(self):
        cleaned_data = super(PeriodForm, self).clean()
        time_of_period = cleaned_data.get("time_of_Period")
        name = cleaned_data.get("name")
        descr = cleaned_data.get("descr")
        if name is not None and time_of_period is not None and descr is not None:
            if not validate_year(time_of_period):
                raise ValidationError('incorect period year validation')
            elif name == None:
                raise ValidationError('name cannot be empty')


class CompousersForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', }), validators=[RegexValidator(regex='\w+')])
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control'}))
    death_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Compousers
        fields = '__all__'

    def clean(self):
        cleaned_data = super(CompousersForm, self).clean()
        name = cleaned_data.get("name")
        birth_date = cleaned_data.get("birth_date")
        death_date = cleaned_data.get("death_date")


'''class PeriodEditFrom(forms.Form):
    period_name = forms.CharField(lable='Period name', max_length = 100)
    period_time = forms.CharField(lable='Period time', max_length = 9)'''
