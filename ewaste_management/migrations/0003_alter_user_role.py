# Generated by Django 4.2.20 on 2025-04-14 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ewaste_management', '0002_ceapplication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('university_community', 'University_Community'), ('campus_expert', 'Campus_Expert'), ('organization_member', 'Organization_Member')], max_length=20),
        ),
    ]
