from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.template.response import TemplateResponse
from django.http import HttpResponse, request, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from .forms import *
from .models import *
from .fusioncharts import FusionCharts
#from .forms import PeriodEditFrom
# Create your views here.


def index(request):
    return TemplateResponse(request, 'search.html', {})


def home_view(request):
    period_values = Period.objects.order_by('time_of_period').values('name')
    context = {'period_names': period_values}

    return render(request, 'music_search/index.html', context)


class PeriodView(generic.ListView):
    model = Period
    template_name = 'music_search/periods.html'

    def get_context_data(self, **kwargs):
        context = super(PeriodView, self).get_context_data(**kwargs)
        period_values = Period.objects.order_by(
            'time_of_period').values('time_of_period', 'name', 'id')
        context['period_list'] = Period.objects.order_by('time_of_period')
        context['header'] = list(period_values[0].keys())[:-1]
        context['content_period'] = list(period_values)
        return context


class CompousersView(generic.ListView):
    model = Compousers
    template_name = 'music_search/compousers.html'

    def chart(self):
        dataSource = {}
        dataSource['chart'] = {
            "caption": "Compousers in Periods chart",
            "numberPrefix": "$",
            "bgColor": "#ffffff",
            "startingAngle": "310",
            "centerLabelBold": "1",
            "showTooltip": "0",
            "decimals": "0",
            "theme": "fusion"
        }
        dataSource['data'] = []

        Renesans_comp = 0
        Baroque_comp = 0
        Classical_comp = 0
        Romatic_comp = 0
        Postmod = 0

        for key in Compousers.objects.all():
            if key.period.name == 'Baroque':
                Baroque_comp += 1
            elif key.period.name == 'Renaissance':
                Renesans_comp += 1
            elif key.period.name == 'Classical':
                Classical_comp += 1
            elif key.period.name == 'Romantic':
                Romatic_comp += 1

        periods = [Classical_comp, Baroque_comp,
                   Romatic_comp, Renesans_comp, Postmod]

        index = 0
        for key in Period.objects.all():
            data = {}
            data['label'] = key.name
            data['value'] = periods[index]
            index += 1
            dataSource['data'].append(data)

        pie2D = FusionCharts(type="doughnut2d", id="ex1", width="550", height="450",
                             renderAt="chart-container", dataFormat="json", dataSource=dataSource)

        return pie2D

    def get_context_data(self, **kwargs):
        context = super(CompousersView, self).get_context_data(**kwargs)
        compouser_values = Compousers.objects.order_by(
            'birth_date').values('name', 'birth_date', 'death_date', 'id')
        index = 0
        for comp in compouser_values:
            c = Compousers.objects.get(pk=comp['id'])
            compouser_values[index]['period'] = c.period.name
            del compouser_values[index]['id']
            compouser_values[index]['id'] = c.id
            index += 1
        context['compousers_list'] = Compousers.objects.order_by('birth_date')
        context['header'] = list(compouser_values[0].keys())[:-1]
        context['content_compousers'] = list(compouser_values)
        context['chart_compousers'] = self.chart().render()
        return context


class DetailView(generic.DetailView):
    model = Period
    template_name = 'music_search/period_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        return context


class CompousersDetailView(generic.DetailView):
    model = Compousers
    template_name = 'music_search/compousers_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CompousersDetailView, self).get_context_data(**kwargs)
        return context


class PeriodCreate(CreateView):
    model = Period
    form_class = PeriodForm
    template_name = 'music_search/period_create.html'
    #fields = ['time_of_period', 'name', 'descr']


class PeriodUpdate(UpdateView):
    model = Period
    form_class = PeriodForm
    template_name = 'music_search/period_edit.html'


class PeriodDelete(DeleteView):
    model = Period
    success_url = reverse_lazy('period-list')


class CompousersCreate(CreateView):
    model = Compousers
    form_class = CompousersForm
    template_name = 'music_search/compousers_create.html'
    #fields = ['time_of_period', 'name', 'descr']


class CompousersUpdate(UpdateView):
    model = Compousers
    form_class = CompousersForm
    template_name = 'music_search/compousers_edit.html'


class CompousersDelete(DeleteView):
    model = Compousers
    success_url = reverse_lazy('period-list')
