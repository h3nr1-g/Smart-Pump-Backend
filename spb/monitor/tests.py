from django.test import TestCase
from django.urls import reverse
from django_webtest import WebTest

from api.models import Pump, TransmittedTiming


def create_pumps():
    Pump.objects.create(
        active=True,
        sleepTime=10,
        activeTime=10,
        description='foobar',
        name='cheeseburger',
        remainingTankVolume=12,
        maxTankVolume=120,
        throughput=2.5,
        power=2.5,
        remainingBatteryCapacity=2000,
        maxBatteryCapacity=4000,
        operatingVoltage=5,
        needsService=False,
    )

    Pump.objects.create(
        active=True,
        sleepTime=10,
        activeTime=10,
        description='foobar',
        name='moep-moep',
        remainingTankVolume=None,
        maxTankVolume=None,
        throughput=2.5,
        power=2.5,
        remainingBatteryCapacity=None,
        maxBatteryCapacity=None,
        operatingVoltage=5,
        needsService=False,
    )


def create_activities():
    for _ in range(10):
        for pump in Pump.objects.all():
            TransmittedTiming.objects.create(
                pump=pump,
                activeTime=pump.activeTime,
                sleepTime=pump.sleepTime,
            )


class OverViewTest(TestCase):
    """
    Test class for the view class OverView
    """
    def setUp(self):
        create_pumps()
        create_activities()

    def test_get_request_all_active(self):
        response = self.client.get(reverse('monitor:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Details' in response.content.decode())
        self.assertTrue('Delete' in response.content.decode())
        self.assertFalse('Deactivated' in response.content.decode())
        self.assertFalse('Service Required' in response.content.decode())
        for pump in Pump.objects.all():
            self.assertTrue(pump.name in response.content.decode())


    def test_get_all_deactivated(self):
        for pump in Pump.objects.all():
            pump.active = False
            pump.save()
        response = self.client.get(reverse('monitor:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Details' in response.content.decode())
        self.assertTrue('Delete' in response.content.decode())
        self.assertFalse('Active' in response.content.decode())
        self.assertFalse('Service Required' in response.content.decode())


class PumpDetailsViewTest(WebTest):
    """
    Test class for the view class PumpDetailsView
    """
    def setUp(self):
        create_pumps()
        create_activities()

    def test_get_invalid_pump(self):
        response = self.client.get(reverse('monitor:pump_details', args=[1234]))
        self.assertEqual(response.status_code, 404)

    def test_get_valid_pump(self):
        response = self.client.get(reverse('monitor:pump_details', args=[Pump.objects.all()[0].id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_invalid_pump(self):
        response = self.client.delete(reverse('monitor:pump_details', args=[1234]))
        self.assertEqual(response.status_code, 404)

    def test_delete_valid_pump(self):
        pid = Pump.objects.all()[0].id
        self.assertTrue(len(Pump.objects.filter(pk=pid))==1)
        response = self.client.delete(reverse('monitor:pump_details', args=[pid]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(Pump.objects.filter(pk=pid)) == 0)

    def test_post_invalid_pump(self):
        response = self.client.post(reverse('monitor:pump_details',args=[1234]))
        self.assertEqual(response.status_code, 404)

    def test_post_empty_data(self):
        pid = Pump.objects.all()[0].id
        response = self.client.post(reverse('monitor:pump_details',args=[pid]),{})
        self.assertEqual(response.status_code, 400)

    def test_post_valid_change(self):
        new_description = 'Moep moep'
        pump = Pump.objects.all()[0]
        self.assertNotEqual(new_description, pump.description)
        form = self.app.get(reverse('monitor:pump_details', args=[pump.id])).form
        form['description'] = new_description
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pump'].description, new_description)

    def test_post_invalid_capacity_change(self):
        pump = Pump.objects.all()[0]
        form = self.app.get(reverse('monitor:pump_details', args=[pump.id])).form
        form['remainingBatteryCapacity'] = pump.maxBatteryCapacity +1
        response = form.submit(status=400)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('Remaining capacity can not be greater' in response.content.decode())

    def test_post_invalid_volume_change(self):
        pump = Pump.objects.all()[0]
        form = self.app.get(reverse('monitor:pump_details', args=[pump.id])).form
        form['remainingTankVolume'] = pump.maxTankVolume +1
        response = form.submit(status=400)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('Remaining water volume can not be greater' in response.content.decode())


class NewPumpViewTest(WebTest):
    """
    Test class for the view class NewPumpView
    """

    def test_get(self):
        response = self.client.get(reverse('monitor:pump_new'))
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_data(self):
        form = self.app.get(reverse('monitor:pump_new')).form
        response = form.submit(status=400)
        self.assertEqual(response.status_code, 400)

    def test_post_valid_data(self):
        form = self.app.get(reverse('monitor:pump_new')).form
        form['name'] = 'Foobar12345'
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        pumps = Pump.objects.filter(name='Foobar12345')
        self.assertEqual(len(pumps),1)


class SignalTest(TestCase):
    """
    Test class for the signal handlers in signals.py
    """

    def setUp(self):
        create_pumps()

