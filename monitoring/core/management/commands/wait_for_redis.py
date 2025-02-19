"""
Django command to wait for the database to be available.
"""
import time


from django.core.management.base import BaseCommand
from redis import RedisError


from core.runtime import RuntimeRegistry


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting for redis ...")

        max_tries = 10
        current_try = 0

        db_up = False
        while db_up is False and current_try < max_tries:
            current_try += 1
            try:
                conn = RuntimeRegistry.get_redis()
                conn.ping()
                db_up = True
            except RedisError as ex:
                self.stdout.write(
                    f"{current_try} Redis unavailable, waiting 1 second..."
                )
                self.stdout.write(str(ex))
                time.sleep(1)

        if not db_up:
            self.stdout.write(
                self.style.ERROR("Redis is not available!")
            )
            exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS("Redis available!")
            )
