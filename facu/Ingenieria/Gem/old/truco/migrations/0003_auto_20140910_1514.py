# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('truco', '0002_auto_20140910_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfiles',
            name='usuario',
            field=models.CharField(max_length=200),
        ),
    ]
