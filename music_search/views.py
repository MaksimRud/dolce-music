from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.template.response import TemplateResponse
from django.http import HttpResponse, request, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import openpyxl
import io
import xlsxwriter
from django.utils.translation import ugettext

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


def post_per_file(request):
    periods = Period.objects.all()
    period_values = Period.objects.order_by(
        'time_of_period').values('time_of_period', 'name', 'id')
    template_name = 'music_search/periods.html'

    print(request)
    print(request.method)
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        uploaded_file_url = fs.url(filename)
        wb = openpyxl.load_workbook(excel_file)
        print(request)
        worksheet = wb["Лист1"]
        print(worksheet)

        period_name = [period['name'] for period in period_values]

        for title in worksheet.iter_rows(min_row=1, max_col=1, values_only=True):
            if "Name" not in title:
                raise ValidationError(
                    "Wrog file information('No period name')")
            else:
                index = 0
                for data in worksheet.iter_rows(min_row=1, max_col=3, values_only=True):
                    index += 1
                    name = data[0]
                    if name == None:
                        break
                    elif name not in period_name:
                        new_model = {
                            'name': data[0], 'time_of_period': data[1], 'descr': data[2]}
                        p = Period(**new_model)
                        p.save()
                    else:
                        for period in period_values:
                            if name not in period:
                                continue
                            else:
                                time_of_period = data[1]
                                descr = data[2]
                                Period.objects.filter(pk=period['id']).update(
                                    time_of_period=time_of_period, descr=descr)
        return render(request, 'music_search/periods.html', {{
            'uploaded_file_url': uploaded_file_url
        }})
    return render(request, 'music_search/periods.html')


def get_per_file(request):
    periods = Period.objects.all()
    template_name = 'music_search/periods.html'

    output = io.BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet("Summary")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'align': 'left',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    if Period:
        period_text = Period.name
    else:
        period_text = ugettext("all recorded towns")

    title_text = ugettext("Periods")
    worksheet_s.merge_range('B2:I2', title_text, title)

    worksheet_s.write(4, 0, ugettext("No"), header)
    worksheet_s.write(4, 1, ugettext("name"), header)
    worksheet_s.write(4, 2, ugettext("time"), header)

    description_col_width = 10

    for idx, data in enumerate(periods):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.name, cell)
        worksheet_s.write_string(row, 2, data.time_of_period, cell_center)
        worksheet_s.write_string(row, 3, data.descr, cell)
        if len(data.descr) > description_col_width:
            description_col_width = len(data.descr)

    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    return response


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

class PieceOfMusicView(generic.ListView):
    model = PieceOfMusic
    template_name = 'music_search/piecemusic.html'

    def get_context_data(self, **kwargs):
        context = super(PieceOfMusicView, self).get_context_data(**kwargs)
        music_values = PieceOfMusicView.objects.order_by(
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
    template_name = 'music_search/period_delete.html'

    def get_success_url(self):
        return reverse('music_search:period')


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
    template_name = 'music_search/compousers_delete.html'

    def get_success_url(self):
        return reverse('music_search:compouser')
