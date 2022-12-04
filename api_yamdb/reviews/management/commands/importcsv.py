import csv
from django.core.management import BaseCommand
from django.utils import timezone
from reviews.models import (Category,
                            Genre,
                            Title,
                            User,
                            GenreTitle,
                            Review)
                            # Comment)


class Command(BaseCommand):
    """Загружает модели в базу данных из файла CSV.\n
    Текст команды: 'python manage.py importcsv D:/Dev/api_yamdb/api_yamdb/static/data/
    (ваш путь к папке с файлами CSV)' 
    """

    def add_arguments(self, parser):
        parser.add_argument("csv_folder_path", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        folder_path = options["csv_folder_path"]

        # Импортируем категории
        with open(f'{folder_path}category.csv', "r", encoding='utf-8') as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                Category.objects.create(
                    id=row[0],
                    name=row[1],
                    slug=row[2]
                )

        # Импортируем жанры
        with open(f'{folder_path}genre.csv', "r", encoding='utf-8') as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                Genre.objects.create(
                    id=row[0],
                    name=row[1],
                    slug=row[2]
                )

        # Импортируем произведения
        with open(f'{folder_path}titles.csv', "r", encoding='utf-8') as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                category = Category.objects.get(pk=row[3])
                Title.objects.create(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category=category
                )

        # Импортируем таблицу связей произведение/жанр
        with open(f'{folder_path}genre_title.csv', "r", encoding='utf-8') as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                GenreTitle.objects.create(
                    title=Title.objects.get(pk=row[1]),
                    genre=Genre.objects.get(pk=row[2])
                )

        # Импортируем таблицу пользователей
        with open(f'{folder_path}users.csv', "r", encoding='utf-8') as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                User.objects.create(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                    bio=row[4],
                    first_name=row[5],
                    last_name=row[6]
                )

        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()}"
                " seconds."
            )
        )

        # Импортируем отзывы на произведения
        with open(f'{folder_path}review.csv', "r", encoding='utf-8') as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                title = Title.objects.get(pk=row[1])
                author = User.objects.get(pk=row[3])
                Review.objects.create(
                    id=row[0],
                    title=title,
                    text=row[2],
                    author=author,
                    score=row[4],
                    pub_date=row[5]
                )