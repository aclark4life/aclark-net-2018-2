from django.test import TestCase
from .models import Time

class AnimalTestCase(TestCase):
    def setUp(self):
        Time.objects.create(log="Competently innovate corporate innovation")


    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        time = Time.objects.get(pk=1)
        self.assertEqual(time.log, "Competently innovate corporate innovation")
