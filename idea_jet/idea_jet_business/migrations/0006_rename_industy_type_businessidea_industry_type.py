# Generated by Django 4.2.1 on 2023-05-24 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('idea_jet_business', '0005_remove_businessidea_finance_model_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='businessidea',
            old_name='industy_type',
            new_name='industry_type',
        ),
    ]
