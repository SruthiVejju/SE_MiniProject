from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create synthetic student accounts up to a target count.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5000,
            help='Target total number of student profiles.'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        target = options['count']
        User = get_user_model()

        existing = UserProfile.objects.filter(
            role=UserProfile.STUDENT
        ).count()

        if existing >= target:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Already have {existing} student profiles.'
                )
            )
            return

        remaining = target - existing
        self.stdout.write(f'Creating {remaining} student accounts...')

        users = [
            User(
                username=f'loadstudent{i:05d}',
                email=f'loadstudent{i:05d}@example.com',
                is_active=True,
            )
            for i in range(1, remaining + 1)
        ]

        User.objects.bulk_create(users, batch_size=500)

        created_users = User.objects.filter(
            username__startswith='loadstudent'
        ).order_by('-id')[:remaining]

        profiles = [
            UserProfile(
                user=user,
                role=UserProfile.STUDENT,
                block='A'
            )
            for user in created_users
        ]

        UserProfile.objects.bulk_create(profiles, batch_size=500)

        total = UserProfile.objects.filter(
            role=UserProfile.STUDENT
        ).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'Success! Total student profiles: {total}'
            )
        )