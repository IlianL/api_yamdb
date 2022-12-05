
import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import Category, Genre, Title, User

from .validators import UsernameValidator

CAT_LIST = list(Category.objects.all())
GEN_LIST = list(Genre.objects.all())
CAT_CHOICES = [(category.slug, category) for category in CAT_LIST]
GEN_CHOICES = [(genre.slug, genre) for genre in GEN_LIST]


class SingUpSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=True
        # validators=[UniqueTogetherValidator(
        #         queryset=User.objects.all(),
        #         fields=['username', 'email'])]
    )
    username = serializers.CharField(
        required=True,
        validators=[UsernameValidator(), ]
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                "Имя пользователя не может быть 'me'"
            )
        return value


class ReceiveTokenSerializer(serializers.Serializer):

    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.ChoiceField(
        choices=CAT_CHOICES
    )

    genre = serializers.MultipleChoiceField(
        choices=CAT_CHOICES
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        """Проверка корректности года выпуска."""
        if value > datetime.datetime.now().year:
            raise serializers.ValidationError(
                'Год выпуска произведения позже текущего!'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class UsersSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='username должен быть уникальным')]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class UserProfileSerializer(UsersSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio')
        read_only_fields = ('role',)
