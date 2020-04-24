from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.template.response import TemplateResponse
from django.http import HttpResponse, request, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.template.defaulttags import register
import openpyxl
import io
import xlsxwriter
from django.utils.translation import ugettext

from .forms import *
from .models import *
from django.db.models import Count
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

    if request.method == 'POST' and request.FILES['excel-file']:
        excel_file = request.FILES['excel-file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        uploaded_file_url = fs.url(filename)
        wb = openpyxl.load_workbook(excel_file)
        print(request)
        worksheet = wb[wb.sheetnames[0]]
        print(worksheet)

        period_name = [period['name'] for period in period_values]

        for index in worksheet.iter_cols(min_row=1, max_col=1, values_only=True):
            print(index)
            for cell in index:
                print(cell)
            i = 0
            for data in worksheet.iter_rows(min_row=1, max_col=4, values_only=True):
                print("Row ", i, " is ", data)
                if i == 0:
                    i += 1
                    continue
                i += 1
                name = data[1]
                print("Name: " + name)
                if name == None:
                    break
                elif name not in period_name:
                    print("name is not in a database.. update!")
                    new_model = {
                        'name': data[1], 'time_of_period': data[2], 'descr': data[3]}
                    p = Period(**new_model)
                    p.save()
                else:
                    print("name is in database")
                    print(period_values)
                    for period in period_values:
                        print(period)
                        if name != period['name']:
                            print(name + " is not in " + period['name'])
                            continue
                        else:
                            print(name + " is in a period. May be edited")
                            time_of_period = data[2]
                            descr = data[3]
                            Period.objects.filter(pk=period['id']).update(
                                time_of_period=time_of_period, descr=descr)
                            print(name + "Was changed")
    period_values = Period.objects.order_by(
        'time_of_period').values('time_of_period', 'name', 'id')
    header = list(period_values[0].keys())[:-1]
    content_period = list(period_values)
    period_list = Period.objects.order_by('time_of_period')

                
    return render(request, 'music_search/periods.html', {
        'uploaded_file_url': uploaded_file_url,
        'header': header,
        'content_period': content_period,
        'period_list': period_list
    })

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

    worksheet_s.write(0, 0, ugettext("No"), header)
    worksheet_s.write(0, 1, ugettext("name"), header)
    worksheet_s.write(0, 2, ugettext("time"), header)
    worksheet_s.write(0, 3, ugettext("descr"), header)

    description_col_width = 10

    for idx, data in enumerate(periods):
        row = 1 + idx
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
    model = Compouser
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

        for key in Period.objects.annotate(num_compousers=Count('compouser')):
            data = {}
            data['label'] = key.name
            data['value'] = key.num_compousers
            dataSource['data'].append(data)

        pie2D = FusionCharts(type="doughnut2d", id="ex1", width="550", height="450",
                             renderAt="chart-container", dataFormat="json", dataSource=dataSource)

        return pie2D

    def get_context_data(self, **kwargs):
        context = super(CompousersView, self).get_context_data(**kwargs)
        compouser_values = Compouser.objects.order_by(
            'birth_date').values('name', 'birth_date', 'death_date', 'id')
        index = 0
        for comp in compouser_values:
            c = Compouser.objects.get(pk=comp['id'])
            compouser_values[index]['period'] = c.period.name
            del compouser_values[index]['id']
            compouser_values[index]['id'] = c.id
            index += 1
        context['compousers_list'] = Compouser.objects.order_by('birth_date')
        context['header'] = list(compouser_values[0].keys())[:-1]
        context['content_compousers'] = list(compouser_values)
        context['chart_compousers'] = self.chart().render()
        return context

def get_comp_file(request):
    comp = Compouser.objects.all()

    template_name = 'music_search/compousers.html'

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

    worksheet_s.write(0, 0, ugettext("No"), header)
    worksheet_s.write(0, 1, ugettext("name"), header)
    worksheet_s.write(0, 2, ugettext("birth_date"), header)
    worksheet_s.write(0, 3, ugettext("death_date"), header)
    worksheet_s.write(0, 4, ugettext("period"), header)

    description_col_width = 10

    for idx, data in enumerate(comp):
        row = 1 + idx
        comp = Compouser.objects.get(pk=data.id)
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.name, cell)
        worksheet_s.write_string(row, 2, str(data.birth_date), cell_center)
        worksheet_s.write_string(row, 3, str(data.death_date), cell)
        worksheet_s.write_string(row, 4, comp.period.name, cell)

    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    return response

def post_comp_file(request):
    comp = Compouser.objects.all()
    comp_values = Compouser.objects.order_by(
        'birth_date').values('name', 'birth_date', 'death_date', 'id')
    
    template_name = 'music_search/compousers.html'

    if request.method == 'POST' and request.FILES['excel-file']:
        excel_file = request.FILES['excel-file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        uploaded_file_url = fs.url(filename)
        wb = openpyxl.load_workbook(excel_file)
        print(request)
        worksheet = wb[wb.sheetnames[0]]
        print(worksheet)

        compouser = [comp['name'] for comp in comp_values]

        for index in worksheet.iter_cols(min_row=1, max_col=1, values_only=True):
            print(index)
            for cell in index:
                print(cell)
            i = 0
            for data in worksheet.iter_rows(min_row=1, max_col=5, values_only=True):
                print("Row ", i, " is ", data)
                if i == 0:
                    i += 1
                    continue
                i += 1
                name = data[1]
                print("Name: " + name)
                if name == None:
                    break
                elif name not in compouser:
                    print("name is not in a database.. update!")
                    period_name = [period['name'] for period in period_values]
                    if data[4] not in period_name:
                        break
                    p = Period.objects.get(name = data[4])
                    new_model = {
                        'name': data[1], 
                        'birth_date': data[2], 
                        'death_date': data[3], 
                        'period': p.id
                    }
                    p = Compouser(**new_model)
                    p.save()
                else:
                    print("name is in database")
                    print(comp_values)
                    for c in comp_values:
                        print(c)
                        if name != c['name']:
                            print(name + " is not in " + c['name'])
                            continue
                        else:
                            print(name + " is in a period. May be edited")
                            birth_date = data[2]
                            death_date = data[3]
                            period = data[4]
                            p = Period.objects.get(name = period)
                            Compouser.objects.filter(pk=c['id']).update(
                                birth_date=birth_date, death_date=death_date, period=p.id)
                            print(name + "Was changed")
    compouser_values = Compouser.objects.order_by(
        'birth_date').values('name', 'birth_date', 'death_date', 'id')
    index = 0
    for comp in compouser_values:
        c = Compouser.objects.get(pk=comp['id'])
        compouser_values[index]['period'] = c.period.name
        del compouser_values[index]['id']
        compouser_values[index]['id'] = c.id
        index += 1
    header = list(compouser_values[0].keys())[:-1]
    content_compouser = list(compouser_values)
    print(content_compouser)
    compouser_list = Compouser.objects.order_by('birth_date')
    
    return render(request, 'music_search/compousers.html', {
        'uploaded_file_url': uploaded_file_url,
        'header': header,
        'content_compousers': content_compouser,
        'compousers_list': compouser_list
    })

class PieceOfMusicView(generic.ListView):
    model = PieceOfMusic
    template_name = 'music_search/music.html'

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

        for key in Compouser.objects.annotate(num_music=Count('pieceofmusic')):
            data = {}
            data['label'] = key.name
            data['value'] = key.num_music
            dataSource['data'].append(data)
              
        pie2D = FusionCharts(type="doughnut2d", id="ex1", width="550", height="450",
                             renderAt="chart-container", dataFormat="json", dataSource=dataSource)

        return pie2D

    def get_context_data(self, **kwargs):
        context = super(PieceOfMusicView, self).get_context_data(**kwargs)
        music_values = PieceOfMusic.objects.order_by(
            'year_written').values('name', 'year_written', 'id')
        index = 0
        print(music_values)
        for mus in music_values:
            m = PieceOfMusic.objects.get(pk=mus['id'])
            music_values[index]['compouser'] = m.compousers.name
            music_values[index]['type_of_piece'] = m.type_of_piece.name
            music_values[index]['year_written'] = str(m.year_written)[:4]
            del music_values[index]['id']
            music_values[index]['id'] = m.id
            index += 1
        context['music_list'] = PieceOfMusic.objects.order_by('year_written')
        context['header'] = list(music_values[0].keys())[:-1]
        context['content_music'] = list(music_values)
        context['chart_music'] = self.chart().render()
        return context

def get_music_file(request):
    music = PieceOfMusic.objects.all()

    template_name = 'music_search/music.html'

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

    worksheet_s.write(0, 0, ugettext("No"), header)
    worksheet_s.write(0, 1, ugettext("name"), header)
    worksheet_s.write(0, 2, ugettext("year_written"), header)
    worksheet_s.write(0, 3, ugettext("compouser"), header)
    worksheet_s.write(0, 4, ugettext("type"), header)


    description_col_width = 10

    for idx, data in enumerate(music):
        row = 1 + idx
        mus = PieceOfMusic.objects.get(pk=data.id)
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.name, cell)
        worksheet_s.write_string(row, 2, str(data.year_written), cell_center)
        worksheet_s.write_string(row, 3, mus.compousers.name, cell)
        worksheet_s.write_string(row, 4, mus.type_of_piece.name, cell)


    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    return response

def post_music_file(request):
    music = PieceOfMusic.objects.all()
    music_values = PieceOfMusic.objects.order_by(
            'year_written').values('name', 'year_written', 'compousers', 'id')
    comp_values = Compouser.objects.values('name')
    type_ = TypeOfPiece.objects.values('name')

    template_name = 'music_search/music.html'
    
    if request.method == 'POST' and request.FILES['excel-file']:
        excel_file = request.FILES['excel-file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        uploaded_file_url = fs.url(filename)
        wb = openpyxl.load_workbook(excel_file)
        print(request)
        worksheet = wb[wb.sheetnames[0]]
        print(worksheet)

        music_name = [mus['name'] for mus in music_values]
        comp_name = [comp['name'] for comp in comp_values]
        type_name = [t['name'] for t in type_]

        for index in worksheet.iter_cols(min_row=1, max_col=1, values_only=True):
            print(index)
            for cell in index:
                print(cell)
            i = 0
            for data in worksheet.iter_rows(min_row=1, max_col=5, values_only=True):
    
                if i == 0:
                    i += 1
                    continue
                i += 1
                name = data[1]
            
                if name == None:
                    break
                elif name not in music_name:
                    print("name is not in a database.. update!")
                    
                    if data[3] not in comp_name or data[4] not in type_name:
                        break
                    t = TypeOfPiece.objects.get(name = data[4])
                    c = Compouser.objects.get(name = data[3])
                    new_model = {
                        'name': data[1], 
                        'year_written': data[2], 
                        'compouser': c.id, 
                        'type': t.id
                    }
                    p = PieceOfMusic(**new_model)
                    p.save()
                else:
                    for c in music_values:
                        print(c)
                        if name != c['name']:
                            print(name + " is not in " + c['name'])
                            continue
                        else:
                            print(name + " is in a period. May be edited")
                            year_written = data[2]
                            p = PieceOfMusic.objects.get(name = data[1])
                            c = Compouser.objects.get(name = data[3])
                            compouser_id = c.id
                            t = TypeOfPiece.objects.get(name = data[4])
                            type_of_piece_id = t.id
                            PieceOfMusic.objects.filter(pk=p.id).update(
                                year_written=year_written, 
                                compousers_id=compouser_id, 
                                type_of_piece_id=type_of_piece_id
                            )
                            print(name + "Was changed")
    music_values = PieceOfMusic.objects.order_by(
            'year_written').values('name', 'year_written', 'id')
    index = 0
    print(music_values)
    for mus in music_values:
        m = PieceOfMusic.objects.get(pk=mus['id'])
        music_values[index]['compouser'] = m.compousers.name
        music_values[index]['type_of_piece'] = m.type_of_piece.name
        music_values[index]['year_written'] = str(m.year_written)[:4]
        del music_values[index]['id']
        music_values[index]['id'] = m.id
        index += 1
    music_list = PieceOfMusic.objects.order_by('year_written')
    header = list(music_values[0].keys())[:-1]
    content_music = list(music_values)
    
    return render(request, 'music_search/music.html', {
        'uploaded_file_url': uploaded_file_url,
        'header': header,
        'content_music': content_music,
        'music_list': music_list
    })

class DetailView(generic.DetailView):
    model = Period
    template_name = 'music_search/period_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        return context


class CompousersDetailView(generic.DetailView):
    model = Compouser
    template_name = 'music_search/compousers_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CompousersDetailView, self).get_context_data(**kwargs)
        return context

class MusicDetailView(generic.DeleteView):
    model = PieceOfMusic
    template_name = 'music_search/music_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MusicDetailView, self).get_context_data(**kwargs)
        music = PieceOfMusic.objects.get(id=self.object.id)
        sheets = music.sheet_set.all()
        sheet = []
        for sh in sheets:
            url = sh.sheet.decode("utf-8")
            if url not in sheet:
                sheet.append(url)
        parts = music.part_set.all()
        audio = []
        for part in parts:
            for audios in part.audios.all():
                url = audios.audio_rec.decode("utf-8")
                if url not in audio:
                    audio.append(url) 
        names = [ part['name'] for part in list(parts.values('name'))]
        context['parts'] = parts
        context['parts_name'] = names
        context['audio'] = audio
        context['sheet'] = sheet
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
    model = Compouser
    form_class = CompousersForm
    template_name = 'music_search/compousers_create.html'
    #fields = ['time_of_period', 'name', 'descr']


class CompousersUpdate(UpdateView):
    model = Compouser
    form_class = CompousersForm
    template_name = 'music_search/compousers_edit.html'


class CompousersDelete(DeleteView):
    model = Compouser
    template_name = 'music_search/compousers_delete.html'

    def get_success_url(self):
        return reverse('music_search:compouser')

class PieceOfMusicCreate(CreateView):
    model = PieceOfMusic
    form_class = MusicForm
    template_name = 'muisc_search/music_create.html'

class PieceOfMusicUpdate(UpdateView):
    model = PieceOfMusic
    form_class = MusicForm
    template_name = 'music_search/music_edit.html'


class PieceOfMusicDelete(DeleteView):
    model = PieceOfMusic
    template_name = 'music_search/music_delete.html'

    def get_success_url(self):
        return reverse('music_search:music')



