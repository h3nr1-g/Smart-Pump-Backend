from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from django_webtest import WebTest
from rest_framework.authtoken.models import Token
from api.models import Pump, TransmittedTiming


def create_pumps():
    Pump.objects.create(
        active=True,
        sleepTime=10,
        activeTime=10,
        description='foobar',
        name='cheeseburger',
        remainingContainerVolume=12,
        maxContainerVolume=120,
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
        remainingContainerVolume=None,
        maxContainerVolume=None,
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


def create_user(username='foo', password='bar'):
    user = User.objects.create_user(
        username=username,
        password=password,
        email='bla@bla.de'
    )
    return user.username, password


class TokenTest(TestCase):
    """
    Test class for the token API key generation
    """

    def setUp(self):
        self.username, self.password = create_user()

    def test_automated_token_generation(self):
        token = Token.objects.get(user=User.objects.get(username=self.username))
        self.assertTrue(len(token.key) > 5)

    def test_token_divergence(self):
        max_dummy_users = 10
        self.assertEqual(len(Token.objects.all()), 1)
        self.assertEqual(len(Token.objects.all()), 1)
        for i in range(max_dummy_users):
            User.objects.create(username=str(i), password=str(i))
        self.assertEqual(len(User.objects.all()), len(Token.objects.all()))
        known_tokens = []
        for token in Token.objects.all():
            self.assertNotIn(token.key, known_tokens)
            known_tokens.append(token.key)

    def test_token_deletion(self):
        self.test_token_divergence()
        for u in User.objects.all():
            u.delete()
        self.assertEqual(len(User.objects.all()), 0)
        self.assertEqual(len(Token.objects.all()), 0)


class OverViewTest(TestCase):
    """
    Test class for the view class OverView
    """

    def setUp(self):
        create_pumps()
        create_activities()
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)
        pump = Pump.objects.all()[0]
        pump.owner = self.user
        pump.save()

    def test_get_unauthorized(self):
        response = self.client.get(reverse('monitor:overview'))
        self.assertEqual(response.status_code, 403)

    def test_get_request_all_user_pumps(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('monitor:overview'))
        self.assertEqual(response.status_code, 200)
        for p in Pump.objects.filter(owner=self.user):
            self.assertIn(p.name, response.content.decode())

        for p in Pump.objects.filter(~Q(owner=self.user)):
            self.assertNotIn(p.name, response.content.decode())


class PumpDetailsViewTest(WebTest):
    """
    Test class for the view class PumpDetailsView
    """

    def setUp(self):
        create_pumps()
        create_activities()
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)
        self.user_pump = Pump.objects.all()[0]
        self.user_pump.owner = self.user
        self.user_pump.save()

    def test_unauthorized_get(self):
        response = self.client.get(reverse('monitor:pump_details', args=[self.user_pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_get_foreign_pump(self):
        self.client.login(username=self.username, password=self.password)
        for p in Pump.objects.filter(~Q(owner=self.user)):
            response = self.client.get(reverse('monitor:pump_details', args=[p.id]))
            self.assertEqual(response.status_code, 403)

    def test_get_own_pump(self):
        self.client.login(username=self.username, password=self.password)
        for p in Pump.objects.filter(owner=self.user):
            response = self.client.get(reverse('monitor:pump_details', args=[p.id]))
            self.assertEqual(response.status_code, 200)
            self.assertIn(p.name, response.content.decode())

    def test_unauthorized_delete(self):
        response = self.client.delete(reverse('monitor:pump_details', args=[self.user_pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_delete_foreign_pump(self):
        self.client.login(username=self.username, password=self.password)
        for p in Pump.objects.filter(~Q(owner=self.user)):
            response = self.client.delete(reverse('monitor:pump_details', args=[p.id]))
            self.assertEqual(response.status_code, 403)

    def test_delete_own_pump(self):
        self.assertTrue(len(Pump.objects.filter(pk=self.user_pump.id)) == 1)
        self.client.login(username=self.username, password=self.password)
        response = self.client.delete(reverse('monitor:pump_details', args=[self.user_pump.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(Pump.objects.filter(pk=self.user_pump.id)) < 1)

    def test_post_unauthorized(self):
        response = self.client.post(reverse('monitor:pump_details', args=[self.user_pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_post_invalid_modification(self):
        self.client.login(username=self.username, password=self.password)
        form = self.app.get(reverse('monitor:pump_details', args=[self.user_pump.id]), user=self.username).form
        form['name'] = ''
        response = form.submit(status=400)
        self.assertEqual(response.status_code, 400)
        pump = Pump.objects.get(pk=self.user_pump.id)
        self.assertGreater(len(pump.name), 1)

    def test_post_foreign_pump(self):
        pump = Pump.objects.filter(~Q(owner=self.user))[0]
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('monitor:pump_details', args=[pump.id]))
        self.assertEqual(response.status_code, 403)

    def test_post_valid_change(self):
        self.client.login(username=self.username, password=self.password)
        form = self.app.get(reverse('monitor:pump_details', args=[self.user_pump.id]), user=self.username).form
        form['name'] = 'HELLO_WORLD'
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        pump = Pump.objects.get(pk=self.user_pump.id)
        self.assertEqual(pump.name, 'HELLO_WORLD')


class NewPumpViewTest(WebTest):
    """
    Test class for the view class NewPumpView
    """

    def setUp(self):
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)

    def test_unauthorized_get(self):
        response = self.client.get(reverse('monitor:pump_new'))
        self.assertEqual(response.status_code, 403)

    def test_authorized_get(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('monitor:pump_new'))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_post(self):
        response = self.client.post(reverse('monitor:pump_new'))
        self.assertEqual(response.status_code, 403)

    def test_post_empty_data(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('monitor:pump_new'),
            {
                'name': '',
                'active': True,
            })
        self.assertEqual(response.status_code, 400)

    def test_post_valid_data(self):
        self.assertEqual(len(Pump.objects.all()), 0)
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            reverse('monitor:pump_new'),
            {
                'name': 'foo',
                'active': True,
                'decription': 'bar',
                'sleepTime': 10,
                'activeTime': 10,
                'remainingContainerVolume': 10,
                'maxContainerVolume': 10,
                'throughput': 123,
                'operatingVoltage': 3.3
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Pump.objects.all()), 1)
        pump = Pump.objects.get(pk=1)
        self.assertEqual(pump.name, 'foo')


class LogoutViewTest(TestCase):
    """
    Test class for the view class LogoutView
    """

    def test_get(self):
        response = self.client.get(reverse('monitor:logout'))
        self.assertEqual(response.status_code, 302)


class LoginViewTest(WebTest):
    """
    test class for the view class LoginView
    """

    def setUp(self):
        self.username, self.password = create_user()
        self.user = User.objects.get(username=self.username)

    def test_get(self):
        response = self.client.get(reverse('monitor:login'))
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_credentials(self):
        form = self.app.get(reverse('monitor:login'), user=self.username).form
        form['username'] = 'aaa'
        form['password'] = 'bbb'
        response = form.submit(status=403)
        self.assertEqual(response.status_code, 403)

    def test_post_empty_credentials(self):
        form = self.app.get(reverse('monitor:login'), user=self.username).form
        response = form.submit(status=400)
        self.assertEqual(response.status_code, 400)

    def test_post_valid_credentials(self):
        form = self.app.get(reverse('monitor:login'), user=self.username).form
        form['username'] = self.username
        form['password'] = self.password
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
