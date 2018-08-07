import json

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from api.models import Pump, ServiceTask
from monitor.tests import create_pumps, create_user, create_activities


class ServiceTaskViewTest(TestCase):
    """
    Test class for the view class ServiceTaskView
    """

    def setUp(self):
        create_pumps()
        self.pump = Pump.objects.all()[0]
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)
        self.pump.owner = self.user
        self.pump.save()
        self.task = ServiceTask.objects.create(
            task='Foobar',
            pump=self.pump
        )

    def test_unauthorized_delete(self):
        response = self.client.delete(reverse('api:service_tasks', args=[self.task.id]))
        self.assertEqual(response.status_code, 403)

    def test_authorized_delete(self):
        self.assertGreater(len(ServiceTask.objects.all()), 0)
        self.client.login(username=self.username, password=self.password)
        response = self.client.delete(reverse('api:service_tasks', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ServiceTask.objects.all()), 0)


class TransmittedTimingsViewTest(TestCase):
    """
    test class for the view class TransmittedTimingsView
    """

    def setUp(self):
        create_pumps()
        create_activities()
        self.pump = Pump.objects.all()[0]
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)
        self.pump.owner = self.user
        self.pump.save()

    def test_unauthorized_get(self):
        response = self.client.get(reverse('api:transmitted_timings', args=[self.pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_get_foreign_timings(self):
        self.client.login(username=self.username, password=self.password)
        pump = Pump.objects.filter(~Q(owner=self.user))[0]
        response = self.client.get(reverse('api:transmitted_timings', args=[pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_get_transmitted_timings(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('api:transmitted_timings', args=[self.pump.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertTrue('data' in data)
        self.assertTrue(isinstance(data['data'], list))
        self.assertGreater(len(data['data']), 0)
        for element in data['data']:
            self.assertTrue('timeStamp' in element)
            self.assertTrue('active' in element)
            self.assertTrue('sleep' in element)


class TimingAggregatorViewTest(TestCase):
    """
    test class for the view class TimingAggregatorView
    """

    def setUp(self):
        create_pumps()
        create_activities()
        self.pump = Pump.objects.all()[0]
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)
        self.pump.owner = self.user
        self.pump.save()

    def test_unauthorized_get(self):
        response = self.client.get(reverse('api:timings_aggregation'))
        self.assertEqual(response.status_code, 403)

    def test_get_timing_aggregations(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('api:timings_aggregation'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertTrue('data' in data)
        self.assertTrue(isinstance(data['data'], list))
        self.assertGreater(len(data['data']), 0)
        foreign_pump = Pump.objects.get(~Q(owner=self.user))
        for element in data['data']:
            self.assertTrue('timeStamp' in element)
            self.assertTrue(self.pump.name in element)
            self.assertFalse(foreign_pump.name in element)


class TimingsViewTest(TestCase):
    """
    test class for the view class TimingsView
    """

    def setUp(self):
        create_pumps()
        self.pump = Pump.objects.all()[0]
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)
        self.pump.owner = self.user
        self.pump.save()

    def test_unauthorized_get(self):
        response = self.client.get(reverse('api:timings', args=[self.pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_get_foreign_timings(self):
        self.client.login(username=self.username, password=self.password)
        pump = Pump.objects.filter(~Q(owner=self.user))[0]
        response = self.client.get(reverse('api:timings', args=[pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_get_timings(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('api:timings', args=[self.pump.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertTrue(isinstance(data, dict))
        self.assertIn('active', data)
        self.assertIn('sleep', data)


class TokenViewTest(TestCase):
    """
    test class for the view class TokenView
    """

    def setUp(self):
        self.username, self.password = create_user()

    def test_unauthorized_get(self):
        response = self.client.get(reverse('api:token'))
        self.assertEqual(response.status_code, 403)

    def test_authorized_get(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('api:token'))
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content.decode())
        self.assertEqual(token['token'], Token.objects.get(user=User.objects.get(username=self.username)).key)

    def test_unauthorized_post(self):
        response = self.client.post(reverse('api:token'))
        self.assertEqual(response.status_code, 403)

    def test_authorized_post(self):
        self.client.login(username=self.username, password=self.password)
        old_token = Token.objects.get(user=User.objects.get(username=self.username)).key
        response = self.client.post(reverse('api:token'))
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content.decode())
        self.assertNotEqual(old_token, token['token'])
