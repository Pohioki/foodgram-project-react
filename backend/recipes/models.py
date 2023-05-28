import unidecode as unidecode
from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.text import slugify

from users.models import User


class Ingredient(models.Model):
    """
    Represents an ingredient used in recipes.
    """

    name = models.CharField(
        max_length=settings.LENGTH_RECIPES,
        verbose_name='Ingredient Name',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=settings.LENGTH_RECIPES,
        verbose_name='Measurement Unit'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]
        ordering = ['name', 'measurement_unit']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """
    Represents a tag associated with recipes.
    """

    name = models.CharField(
        verbose_name='Tag Name',
        max_length=settings.LENGTH_RECIPES,
        db_index=True,
        unique=True,
    )
    color = ColorField(
        verbose_name='HEX Code',
        format='hex',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Check the input format',
            )
        ],
    )
    slug = models.SlugField(
        max_length=settings.LENGTH_RECIPES,
        verbose_name='Slug',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            name_without_accents = unidecode.unidecode(self.name)
            self.slug = slugify(name_without_accents)
        super().save(*args, **kwargs)

    def generate_unique_slug_suffix(self, slug_base):
        queryset = self.__class__.objects.filter(slug__startswith=slug_base)
        existing_slugs = queryset.values_list('slug', flat=True)
        suffix = 1
        new_slug = slug_base
        while new_slug in existing_slugs:
            suffix += 1
            new_slug = f'{slug_base}-{suffix}'
        return f'-{suffix}' if suffix > 1 else ''


class Recipe(models.Model):
    """
    Represents a recipe created by a user.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Recipe Author',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Recipe Name',
        max_length=settings.LENGTH_RECIPES,
    )
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Image'
    )
    text = models.TextField(verbose_name='Description')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ingredients',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking Time',
        validators=[
            MinValueValidator(
                settings.ONE_MINUTE,
                message='Cooking time should be at least 1 minute'
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME,
                message='Cooking time should not exceed 32000 minutes'
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication Date',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class FavoriteShoppingCart(models.Model):
    """
    Abstract base model representing a favorite or shopping cart item.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]
        ordering = ['user', 'recipe']

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(FavoriteShoppingCart):
    """
    Represents a favorite recipe for a user.
    """

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        ordering = ['user', 'recipe']


class ShoppingCart(FavoriteShoppingCart):
    """
    Represents a recipe added to the shopping cart by a user.
    """

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_list'
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        ordering = ['user', 'recipe']


class IngredientRecipe(models.Model):
    """
    Represents the relationship between ingredients and recipes.
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(settings.ONE_INGREDIENT)],
        verbose_name='Amount'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount} ' \
               f'{self.ingredient.measurement_unit}'
