# Generated by Django 4.2.2 on 2023-06-21 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_rename_starting_bid_listing_current_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='state',
            field=models.BooleanField(default=True),
        ),
    ]
