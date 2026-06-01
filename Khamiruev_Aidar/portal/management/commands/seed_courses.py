from django.core.management.base import BaseCommand

from portal.models import Course


class Command(BaseCommand):
    help = 'Заполняет базу демонстрационными курсами'

    def handle(self, *args, **options):
        courses = [
            (Course.TYPE_QUALIFICATION, 'Цифровая грамотность педагога'),
            (Course.TYPE_QUALIFICATION, 'Основы проектного менеджмента'),
            (Course.TYPE_RETRAINING, 'Веб-разработчик'),
            (Course.TYPE_RETRAINING, 'Системный администратор'),
            (Course.TYPE_SAFETY, 'Охрана труда для руководителей'),
            (Course.TYPE_SAFETY, 'Пожарно-технический минимум'),
        ]
        created = 0
        for course_type, title in courses:
            _, was_created = Course.objects.get_or_create(
                course_type=course_type,
                title=title,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Добавлено курсов: {created}'))
