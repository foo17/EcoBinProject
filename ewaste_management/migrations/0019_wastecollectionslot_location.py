# Generated by Django 4.2.20 on 2025-04-28 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ewaste_management', '0018_remove_wastecollectionslot_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='wastecollectionslot',
            name='location',
            field=models.CharField(default='Default Location', max_length=255),
            preserve_default=False,
        ),
    ]
