# Generated by Django 3.2 on 2021-05-24 18:03

import bookwyrm.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookwyrm", "0075_announcement"),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='preview_image',
            field=bookwyrm.models.fields.ImageField(blank=True, null=True, upload_to='cover_previews/'),
        ),
    ]
