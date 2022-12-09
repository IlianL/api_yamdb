from core.mixins import ListCreateDestroy
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .permissions import (AdminOrReadOnly, IsAdmin,
                          IsAuthorAdminModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReadTitleSerializer,
                          ReceiveTokenSerializer, ReviewSerializer,
                          SingUpSerializer, UserProfileSerializer,
                          UsersSerializer, WriteTitleSerializer)


class SignUp(views.APIView):
    """Получить код подтверждения на переданный email."""

    def post(self, request):
        serializer = SingUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            username=serializer.validated_data.get('username'),
            email=serializer.validated_data.get('email')
        )

        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения api_yamdb',
            f'Ваш код подтверждения: "{confirmation_code}"',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceiveToken(views.APIView):
    """Получение токена при регистрации."""

    def post(self, requset):
        serializer = ReceiveTokenSerializer(data=requset.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response({
            'confirmation_code': 'Вы ввели неверный confirmation_code'
        },
            status=status.HTTP_400_BAD_REQUEST)


class TitleViewSet(viewsets.ModelViewSet):
    """Просмотр, создание, редактирование и удаление произведений"""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReadTitleSerializer
        return WriteTitleSerializer


class CategoryViewSet(ListCreateDestroy):
    """Просмотр, создание и удаление категорий произведений"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroy):
    """Просмотр, создание и удаление категорий произведений"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class UsersViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdmin]
    lookup_field = ('username')

    @action(
        methods=['get', 'patch'], url_path='me', detail=False,
        permission_classes=[permissions.IsAuthenticated])
    def user_profile(self, request):
        user = User.objects.get(username=request.user)
        if request.method == 'PATCH':
            serializer = UserProfileSerializer(user, data=request.data,
                                               partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(created_by='admin')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorAdminModeratorOrReadOnly)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorAdminModeratorOrReadOnly)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)
