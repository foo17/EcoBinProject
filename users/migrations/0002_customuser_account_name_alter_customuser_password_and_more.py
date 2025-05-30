# Generated by Django 4.2.20 on 2025-03-26 07:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='account_name',
            field=models.CharField(default='user', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='universitycommunitymember',
            name='university',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='users.university'),
        ),
    ]
