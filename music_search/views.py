from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponse, request, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from .models import *
#from .forms import PeriodEditFrom
# Create your views here.


def index(request):
    return HttpResponse("Hellom, client. You are at the search index.")


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


class DetailView(generic.DetailView):
    model = Period
    template_name = 'music_search/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        return context



class EditView(generic.DetailView):
    model = Period
    template_name = 'music_search/edit.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        return context


class PeriodCreate(CreateView):
    model = Period
    template_name = 'create'
    fields = ['time_of_period', 'name', 'descr']


class PeriodUpdate(UpdateView):
    model = Period
    template_name = 'music_search/edit.html'
    fields = ['descr']


class PeriodDelete(DeleteView):
    model = Period
    success_url = reverse_lazy('period-list')

