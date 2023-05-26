from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngridientFilter(SearchFilter):
    """
     Filter class for Ingredient model based on the name field.

     Attributes:
         search_param (str): The parameter used for searching, set to 'name'.

     Meta:
         model (Ingredient): The model to which the filter is applied.
         fields (tuple): The fields on which the filtering is performed,
         set to ('name',).
     """
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """
    Filter class for Recipe model.

    Attributes:
        tags (filters.ModelMultipleChoiceFilter): Filter for tags based
        on slug field.

        is_favorited (filters.NumberFilter): Filter for favorited recipes.

        is_in_shopping_cart (filters.NumberFilter): Filter for recipes
        in shopping cart.

    Meta:
        model (Recipe): The model to which the filter is applied.
        fields (tuple): The fields on which the filtering is performed,
        including 'tags', 'is_favorited', and 'is_in_shopping_cart'.
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, queryset, value, *args, **kwargs):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value, *args, **kwargs):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return
