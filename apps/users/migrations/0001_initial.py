# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.core.validators
from django.conf import settings
import tinymce.models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username', error_messages={'unique': 'A user with that username already exists.'}, unique=True, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('create_time', models.DateTimeField(null=True, auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(null=True, auto_now=True, verbose_name='更新时间')),
                ('delete', models.SmallIntegerField(default=0, verbose_name='是否删除')),
                ('groups', models.ManyToManyField(blank=True, verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', to='auth.Group', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(blank=True, verbose_name='user permissions', help_text='Specific permissions for this user.', related_name='user_set', to='auth.Permission', related_query_name='user')),
            ],
            options={
                'db_table': 'df_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('create_time', models.DateTimeField(null=True, auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(null=True, auto_now=True, verbose_name='更新时间')),
                ('delete', models.SmallIntegerField(default=0, verbose_name='是否删除')),
                ('receiver_name', models.CharField(max_length=20, verbose_name='收件人')),
                ('receiver_mobile', models.CharField(max_length=11, verbose_name='联系电话')),
                ('detail_addr', models.CharField(max_length=256, verbose_name='详细地址')),
                ('zip_code', models.CharField(max_length=6, null=True, verbose_name='邮政编码')),
                ('is_default', models.BooleanField(verbose_name='默认地址', default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='所属用户')),
            ],
            options={
                'db_table': 'df_address',
            },
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('create_time', models.DateTimeField(null=True, auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(null=True, auto_now=True, verbose_name='更新时间')),
                ('delete', models.SmallIntegerField(default=0, verbose_name='是否删除')),
                ('gender', models.SmallIntegerField(default=0, choices=[(0, '男'), (1, '女')])),
                ('desc', tinymce.models.HTMLField(null=True, verbose_name='商品描述')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
