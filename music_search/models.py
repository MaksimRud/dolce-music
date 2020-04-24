# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.forms import ModelForm
from django.urls import reverse
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
import os
from .validators import *


class Period(models.Model):
    # Field name made lowercase.
    time_of_period = models.CharField(
        db_column='Time_of_Period', max_length=10, validators=[RegexValidator(regex='^[1-9]([0-9]{3})[-][1-9]([0-9]{3})$'), validate_year])
    # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45)
    # Field name made lowercase.
    descr = models.CharField(db_column='Descr', max_length=1000)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('music_search:detail_period', kwargs={'pk': self.pk})

    class Meta:
        managed = False
        db_table = 'period'


class Compouser(models.Model):
    # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=45)
    # Field name made lowercase.
    birth_date = models.DateField(db_column='Birth_Date')
    # Field name made lowercase.
    death_date = models.DateField(
        db_column='Death_Date', blank=True, null=True)
    # Field name made lowercase.
    period = models.ForeignKey(
        Period, on_delete=models.CASCADE, db_column='Period_id')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('music_search:detail_compouser', kwargs={'pk': self.pk})

    class Meta:
        managed = False
        db_table = 'compouser'
        unique_together = (('id', 'period'),)


class TypeOfPiece(models.Model):
    # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=45)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'type_of_piece'


class PieceOfMusic(models.Model):
    # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=45)
    # Field name made lowercase. This field type is a guess.
    year_written = models.DateField(db_column='Year_written')
    # Field name made lowercase.
    compousers = models.ForeignKey(
        Compouser, on_delete=models.CASCADE, db_column='Compousers_id')
    # Field name made lowercase.
    type_of_piece = models.ForeignKey(
        TypeOfPiece, on_delete=models.CASCADE, db_column='Type_of_piece_id')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('music_search:detail_music', kwargs={'pk': self.pk})

    class Meta:
        managed = False
        db_table = 'piece_of_music'
        unique_together = (('id', 'compousers', 'type_of_piece'),)

class Part(models.Model):
    # Field name made lowercase.
    name = models.CharField(
        db_column='Name', 
        max_length=45
    )
    # Field name made lowercase.
    piece_of_music = models.ForeignKey(
        PieceOfMusic, 
        on_delete=models.CASCADE, 
        db_column='Piece_of_Music_id'
    )
    instruments = models.ManyToManyField(
        'Instrument',
        through='InstrumentHasPart', 
        through_fields=('part', 'instrument'),
    )
    audios = models.ManyToManyField(
        'Audio', 
        through='AudioHasPart', 
        through_fields=('part', 'audio')
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'part'
        unique_together = (('id', 'piece_of_music'),)

class Instrument(models.Model):
    # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=45)
    
    parts = models.ManyToManyField(Part, through='InstrumentHasPart', through_fields=('instrument', 'part'))

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'instrument'

class Audio(models.Model):
    # Field name made lowercase.
    audio_rec = models.FileField(db_column='Audio_rec')
    
    parts = models.ManyToManyField(Part, through='AudioHasPart', through_fields=('audio', 'part'))

    class Meta:
        managed = False
        db_table = 'audio'        

class AudioHasPart(models.Model):
    # Field name made lowercase.
    audio = models.ForeignKey(
        Audio, 
        on_delete=models.CASCADE, 
        db_column='Audio_id'
    )
    # Field name made lowercase.
    part = models.ForeignKey(
        Part, 
        on_delete=models.CASCADE,
        db_column='Part_id'
    )

    class Meta:
        managed = False
        db_table = 'audio_has_part'
        unique_together = (('audio', 'part'),)


class InstrumentHasPart(models.Model):
    
    # Field name made lowercase.
    part = models.ForeignKey(
        Part, 
        on_delete=models.CASCADE,
        db_column='Part_id'
    )

    instrument = models.ForeignKey(
        Instrument, 
        on_delete=models.CASCADE, 
        db_column='Instrument_id'
    )

    class Meta:
        managed = False
        db_table = 'instrument_has_part'
        unique_together = (('instrument', 'part'),)


class Sheet(models.Model):
    # Field name made lowercase.
    sheet = models.FileField(db_column='Sheet', upload_to='sheet/%Y/%m/%d/')
    # Field name made lowercase.
    music = models.ForeignKey(
        PieceOfMusic, on_delete=models.CASCADE, db_column='Music_id')

    class Meta:
        managed = False
        db_table = 'sheet'


class MusicianOrOrcestra(models.Model):
    # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=45)
    # Field name made lowercase.
    audio = models.ForeignKey(
        Audio, on_delete=models.CASCADE, db_column='Audio_id')

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'musician or orcestra'
##
#
#   USERS
#

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_staff=False, is_admin=False, is_active=True):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have an password")
        user_obj = self.model(
            email = self.normalize_email(email)
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None):
        user_obj =self.create_user(
            email,
            password=password,
            is_staff=True
        )
        return user_obj

    def create_superuser(self, email, password=None):
        user_obj =self.create_user(
            email,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user_obj
    
    def get_by_natural_key(self, email_):
        return self.get(email=email_)

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique = True)
    active = models.BooleanField(default=True) #can login
    staff = models.BooleanField(default=False) #staff non superuser
    admin = models.BooleanField(default=False) #admin
    # full_name = models.CharField(max_length=255, blank=True, null=True) #superuser
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email' #username
    # email and password are required by default
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_lable):
        return True
    

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property 
    def is_active(self):
        return self.active

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # extend extra data

##
#
#
# DJANGO AUTH MODELS


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

##
# DJANGO DJANGO MODELS
#
#


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        'DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
