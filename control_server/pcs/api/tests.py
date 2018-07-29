import json

from django.test import TestCase
from django.urls import reverse

from api.models import Pump, ServiceTask, TransmittedTiming
from monitor.tests import create_pumps, create_activities


class ServiceTaskViewTask(TestCase):
    """
    Test class for the view class ServiceTaskView
    """
    def setUp(self):
        create_pumps()
        self.pump = Pump.objects.all()[0]
        for i in range(2):
            ServiceTask.objects.create(pump=self.pump,task='foo')
        self.pump.needsService = True
        self.pump.save()


    def test_delete(self):
        self.assertTrue(self.pump.needsService)
        for task in ServiceTask.objects.filter(pump=self.pump):
            response = self.client.delete(reverse('api:service_task',args=[task.id]))
            self.assertEqual(response.status_code, 200)
        self.assertFalse(Pump.objects.get(pk=self.pump.id).needsService)


class TimingsViewTest(TestCase):
    """
    Test class for the view method TimingsView
    """

    def setUp(self):
        create_pumps()

    def test_get(self):
        old_len = len(TransmittedTiming.objects.all())
        pump = Pump.objects.all()[0]
        response = self.client.get(reverse('api:timings', args=[pump.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertTrue('active' in data.keys())
        self.assertTrue('sleep' in data.keys())
        self.assertNotEqual(len(TransmittedTiming.objects.all()), old_len)


class ActivityAggregatorViewTest(TestCase):
    """
    Test class for the view class ActivitiyAggregatorView
    """
    def setUp(self):
        create_pumps()
        create_activities()

    def test_get(self):
        response = self.client.get(reverse('api:timings_aggregation'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        fields = ['xkey', 'ykeys', 'labels', 'data']
        for f in fields:
            self.assertTrue(f in data)
        for pump in Pump.objects.all():
            self.assertTrue(pump.name in data['labels'])

        self.assertTrue(isinstance(data['data'],list))
        for element in data['data']:
            self.assertTrue('timeStamp' in element)

class PumpActivityViewTest(TestCase):
    """
    Test class for PumpActivityView view class
    """
    def setUp(self):
        create_pumps()
        create_activities()

    def test_get(self):
        pump = Pump.objects.all()[0]
        response = self.client.get(reverse('api:transmitted_timings',args=[pump.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        fields = ['xkey', 'ykeys', 'labels', 'data']
        for f in fields:
            self.assertTrue(f in data)
        self.assertTrue(len(data['data']) > 0)



