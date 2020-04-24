from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import *

admin.site.register(Period)
admin.site.register(Compouser)
admin.site.register(PieceOfMusic)
admin.site.register(TypeOfPiece)
admin.site.register(Sheet)
admin.site.register(MusicianOrOrcestra)

class AudioHasPart_inline(admin.TabularInline):
    model = AudioHasPart
    extra = 1

class InstrumentHasPart_inline(admin.TabularInline):
    model = InstrumentHasPart
    extra = 1

class InstrumentAdmin(admin.ModelAdmin):
    inlines = (InstrumentHasPart_inline, )

class AudioAdmin(admin.ModelAdmin):
    inlines = (AudioHasPart_inline, )

class PartAdmin(admin.ModelAdmin):
    inlines = (AudioHasPart_inline, InstrumentHasPart_inline, )

admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(InstrumentHasPart)
admin.site.register(AudioHasPart)



