from django.test import TestCase
from .models import Time


class TimeEntryTestCase(TestCase):
    def setUp(self):
        Time.objects.create(log="Competently innovate corporate innovation")

    def test_time_entry_log(self):
        """
        """
        time = Time.objects.get(pk=1)
        self.assertEqual(time.log, "Competently innovate corporate innovation")
