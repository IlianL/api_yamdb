
import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import Category, Genre, Title, User, Review

from .validators import UsernameValidator


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
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
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
        fields = '__all__'
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
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


class ReviewSerializer(serializers.ModelSerializer):
    """Изменение данных отзыва."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate_correct_score(self, value):
        if 1 <= value <= 10:
            raise serializers.ValidationError('Поставьте оценку от 1 до 10.')
        return value

    def validate_unique_name(self, data):
        request = self.context['request']
        author = request.user
        title = self.context.get('view').kwargs.get('title_id')
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise serializers.ValidationError(
                'Вы можете написать только один отзыв к данному произведению.'
            )
        return data

    class Meta:
        model = Review
        fields = '__all__'
