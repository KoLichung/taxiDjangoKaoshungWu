from django.conf import settings
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):

    def handle(self, *args, **options):
        test_str = "test string"

        with open('test.txt', 'w', encoding='utf-8') as f:
            f.write(test_str)

        cur_path = os.getcwd()
        print(cur_path)
        new_path = os.path.relpath('.//app//test.txt', cur_path)
        print(new_path)
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(test_str)