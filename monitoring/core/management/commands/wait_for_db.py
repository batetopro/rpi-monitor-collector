"""
Django command to wait for the database to be available.
"""
import time


from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write("Waiting for database...")

        max_tries = 10
        current_try = 0

        db_up = False
        while db_up is False and current_try < max_tries:
            current_try += 1
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError):
                self.stdout.write(
                    f"{current_try} Database unavailable, waiting 1 second..."
                )
                time.sleep(1)

        if not db_up:
            self.stdout.write(
                self.style.ERROR("Database is not available!")
            )
            exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS("Database available!")
            )
