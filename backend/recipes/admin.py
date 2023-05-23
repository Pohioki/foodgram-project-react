from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    """
    Inline admin for managing ingredients in a recipe.

    """
    model = IngredientRecipe
    extra = 3
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Recipe model.

    """
    list_display = ('author', 'name', 'cooking_time',
                    'get_favorites', 'get_ingredients',)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientInline,)
    empty_value_display = '-empty-'

    def get_favorites(self, obj):
        """
        Get the number of favorites for a recipe.

        Parameters:
            obj (Recipe): The Recipe instance.

        Returns:
            int: The number of favorites.

        """
        return obj.favorites.count()

    get_favorites.short_description = 'Favorites'

    def get_ingredients(self, obj):
        """
        Get a comma-separated list of ingredients for a recipe.

        Parameters:
            obj (Recipe): The Recipe instance.

        Returns:
            str: The comma-separated list of ingredients.

        """
        return ', '.join([
            ingredient.name for ingredient
            in obj.ingredients.all()])

    get_ingredients.short_description = 'Ingredients'


class IngredientAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Ingredient model.

    """
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Tag model.

    """
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    empty_value_display = '-empty-'


class FavoriteAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Favorite model.

    """
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-empty-'


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ShoppingCart model.

    """
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user',)
    empty_value_display = '-empty-'


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
