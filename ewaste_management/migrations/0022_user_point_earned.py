# Generated by Django 4.2.20 on 2025-04-28 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ewaste_management', '0021_movementrecord_recipeint_company_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='point_earned',
            field=models.IntegerField(default=0),
        ),
    ]
