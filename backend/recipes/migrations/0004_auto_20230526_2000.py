# Generated by Django 3.2.16 on 2023-05-26 17:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230523_1415'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'default_related_name': 'favorites', 'ordering': ['user', 'recipe'], 'verbose_name': 'Favorite', 'verbose_name_plural': 'Favorites'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name', 'measurement_unit'], 'verbose_name': 'Ingredient', 'verbose_name_plural': 'Ingredients'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shopping_list', 'ordering': ['user', 'recipe'], 'verbose_name': 'Shopping Cart', 'verbose_name_plural': 'Shopping Carts'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Cooking time should be at least 1 minute'), django.core.validators.MaxValueValidator(32000, message='Cooking time should not exceed 32000 minutes')], verbose_name='Cooking Time'),
        ),
    ]