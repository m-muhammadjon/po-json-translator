from unittest.mock import patch

from django.core.files import File as DjangoFile
from django.test import TestCase

from main.models import File
from main.tasks import (generate_translated_json_task,
                        generate_translated_po_task)


class GenerateTranslatedFileTaskTest(TestCase):
    @patch("main.tasks.po.generate_translated_po_task")
    def test_task_success_po(self, mock_task):
        # create a test file object
        with DjangoFile(open("test_files/django.po", "rb")) as f:
            file = File(
                from_lang="uz",
                to_lang="en",
                file=f,
                status="Pending",
            )
            file.file.save("django.po", f, save=True)

        # call the task
        generate_translated_po_task(file.id)

        # assert that the file object has been updated correctly
        file.refresh_from_db()
        self.assertEqual(file.status, "Completed")
        self.assertIsNotNone(file.result_file)

    @patch("main.tasks.json.generate_translated_json_task")
    def test_task_success_json(self, mock_task):
        # create a test file object
        with DjangoFile(open("test_files/test.json", "rb")) as f:
            file = File(
                from_lang="uz",
                to_lang="en",
                file=f,
                status="Pending",
            )
            file.file.save("django.po", f, save=True)

        # call the task
        generate_translated_json_task(file.id)

        # assert that the file object has been updated correctly
        file.refresh_from_db()
        self.assertEqual(file.status, "Completed")
        self.assertIsNotNone(file.result_file)
