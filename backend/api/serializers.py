from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import User


class UserSerializer(UserSerializer):
    """
    Serializer class for User model.

    Attributes:
        is_subscribed: Boolean field indicating
        if the user is subscribed to the current user.

    """
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        """
        Get the subscription status of the user.

        Args:
            obj: The User object being serialized.

        returns:
            bool: True if the user is subscribed, False otherwise.

        """
        if self.context['request'].user.is_authenticated:
            return obj.following.filter(
                user=self.context['request'].user
            ).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """
    Serializer class for creating a new user.

    """
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class SubscribeListSerializer(UserSerializer):
    """
    Serializer class for subscribing to a user.

    """
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        """
        Validate the subscription request.

        Check if the user is already subscribed to the author and
        if the user is trying to subscribe to themselves.

        """
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail='Subscription already exists',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail="You can't subscribe to yourself",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj):
        """
        Get the count of recipes for the user.

        """
        return obj.recipes.count()

    def get_recipes(self, obj):
        """
        Get the user's recipes.

        Optionally limit the number of recipes returned
        based on the 'recipes_limit' query parameter.

        """
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = obj.recipes.all()[:int(
            limit)] if limit else obj.recipes.all()
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer class for Tag model.

    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer class for Ingredient model.

    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer class for the relationship between ingredients and recipes.

    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Serializer class for reading recipe details.

    """
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredient_to_recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time'
                  )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(user=request.user).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer class for creating a recipe.

    """

    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Specified tag does not exist'}
    )
    image = Base64ImageField(max_length=None)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    text = serializers.CharField()
    name = serializers.CharField(max_length=254)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Specified tag does not exist')
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < settings.ONE_MINUTE:
            raise serializers.ValidationError(
                'Cooking time should be at least 1 minute'
            )
        if cooking_time > settings.MAX_COOKING_TIME:
            raise serializers.ValidationError(
                'Cooking time cannot exceed 32000 minutes'
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        ingredient_ids = set()
        if not ingredients:
            raise serializers.ValidationError('Ingredients are missing')
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError('Ingredients must be unique')
            ingredient_ids.add(ingredient_id)
            amount = ingredient.get('amount')
            if amount is not None and int(amount) < settings.ONE_INGREDIENT:
                raise serializers.ValidationError(
                    'Ingredient amount must be greater than 0'
                )
            if amount > settings.MAX_INGREDIENTS_COUNT:
                raise serializers.ValidationError(
                    'Ingredient amount must be smaller than 32000'
                )
        return ingredients

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient_data in ingredients:
            ingredient = IngredientRecipe(
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'],
                recipe=recipe,
            )
            ingredient_list.append(ingredient)
        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        instance.ingredients.clear()
        ingredients = validated_data.get('ingredients')
        if ingredients:
            for ingredient_data in ingredients:
                ingredient_id = ingredient_data.get('id')
                amount = ingredient_data.get('amount')
                delete = ingredient_data.get('delete', False)
                if ingredient_id:
                    ingredient = Ingredient.objects.get(id=ingredient_id.id)
                    if delete:
                        instance.ingredients.remove(ingredient)
                    else:
                        instance.ingredients.add(
                            ingredient, through_defaults={'amount': amount})

        tags = validated_data.get('tags')
        if tags:
            instance.tags.set(tags)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Serializer class for representing a short version of a recipe.

    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer class for handling favorites.

    """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """
        Validate the data for favorite serialization.

        Parameters:
            data (dict): The input data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the recipe is already added
            to favorites.

        """
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Recipe is already added to favorites.')
        return data

    def to_representation(self, instance):
        """
        Convert the favorite instance to its serialized representation.

        Parameters:
            instance (Favorite): The Favorite instance.

        Returns:
            dict: The serialized representation of the associated recipe.

        """
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Serializer class for handling the shopping cart.

    """

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """
        Validate the data for shopping cart serialization.

        Parameters:
            data (dict): The input data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the recipe is already added
            to the shopping cart.

        """
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Recipe is already added to the shopping cart.')
        return data

    def to_representation(self, instance):
        """
        Convert the shopping cart instance to its serialized representation.

        Parameters:
            instance (ShoppingCart): The ShoppingCart instance.

        Returns:
            dict: The serialized representation of the associated recipe.

        """
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
