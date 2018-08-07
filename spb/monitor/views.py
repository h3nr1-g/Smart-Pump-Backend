from django.contrib.auth import logout, authenticate, login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.authtoken.models import Token
from api.models import Pump, ServiceTask
from monitor.decorators import user_is_authenticated
from monitor.forms import PumpModelForm, LoginForm
from monitor.tables import PumpTable


@method_decorator(user_is_authenticated, name='dispatch')
class OverView(View):
    """
    View class shows a system overview
    """

    def get(self, request):
        """
        Handler method for GET requests

        :param request: Request object
        :return: HTML overview page
        """
        context = {
            'table': PumpTable(Pump.objects.filter(owner=request.user)),
            'title': 'Pump Overview',
            'token': Token.objects.get(user=request.user).key
        }
        return render(request, 'monitor/overview.html', context)


@method_decorator(user_is_authenticated, name='dispatch')
class PumpDetailsView(View):
    """
    View class for displaying, modification and deletion of pumps and pump details
    """

    def get(self, request, pid):
        """
        Handler method for GET requests

        :param request: Request object
        :param pid: Pump ID
        :return: HTML page with details about one specific pump
        """
        pump = get_object_or_404(Pump, pk=pid)
        if pump.owner != request.user:
            raise PermissionDenied()

        form = PumpModelForm(instance=pump)
        context = {
            'title': 'Pump {}'.format(pump),
            'form': form,
            'pump': pump,
            'tasks': ServiceTask.objects.filter(pump=pump),
            'token': Token.objects.get(user=request.user).key
        }
        return render(request, 'monitor/pump_details.html', context)

    def delete(self, request, pid):
        """
        Handler method for DELETE requests

        :param request: Request object
        :param pid: Pump ID
        :return: Empty 200-OK response on success
        """
        pump = get_object_or_404(Pump, pk=pid)
        if pump.owner != request.user:
            raise PermissionDenied()

        pump.delete()
        return HttpResponse()

    def post(self, request, pid):
        """
        Handler method for POST requests

        :param request: Request object
        :param pid: Pump ID
        :return: HTML page with updated information
        """
        pump = get_object_or_404(Pump, pk=pid)
        if pump.owner != request.user:
            raise PermissionDenied()

        form = PumpModelForm(request.POST, instance=pump)
        context = {
            'title': 'Pump - {}'.format(pump),
            'form': form,
            'pump': pump,
            'tasks': ServiceTask.objects.filter(pump=pump),
            'token': Token.objects.get(user=request.user).key
        }
        if form.is_valid():
            context['success_notification'] = 'Changes saved.'
            form.save()
            return render(request, 'monitor/pump_details.html', context)

        template = loader.get_template('monitor/pump_details.html')
        return HttpResponseBadRequest(template.render(context, request))


@method_decorator(user_is_authenticated, name='dispatch')
class NewPumpView(View):
    """
    View class for the creation of a new pump
    """

    def get(self, request):
        """
        Handler method for GET requests

        :param request: Request object
        :return: HTML for the creation/registration of a new pump
        """
        context = {
            'form': PumpModelForm(),
            'title': 'New Pump'
        }
        return render(request, 'monitor/pump_details.html', context)

    def post(self, request):
        """
        Handler method for POST requests

        :param request: Request object
        :return: HTTP redirect response on success
        """
        form = PumpModelForm(request.POST)

        if form.is_valid():
            pump = form.save()
            return HttpResponseRedirect(reverse('monitor:pump_details', args=[pump.id]))

        template = loader.get_template('monitor/pump_details.html')
        return HttpResponseBadRequest(template.render({'form': form}, request))


class LoginView(View):
    """
    View class for the authentication procedure of a user via the login form
    """

    def get(self, request):
        """
        Handler method for GET requests
        :param request: request object
        :return: 200-OK response with the login page
        """
        context = {
            'form': LoginForm(),
            'title': 'Login'
        }
        return render(request, 'monitor/login.html', context)

    def post(self, request):
        """
        Handler method for POST requests
        :param request: request object
        :return: 302-Redirect response if the login procedure was successful else 400-BadRequest response
        with the form in it
        """
        context = {
            'title': 'Login',
            'failure': True,
            'form': LoginForm(request.POST)
        }

        if context['form'].is_valid():
            user = authenticate(username=context['form'].cleaned_data['username'],
                                password=context['form'].cleaned_data['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('monitor:overview'))
            else:
                template = loader.get_template('monitor/login.html')
                return HttpResponseForbidden(template.render(context, request))
        else:
            template = loader.get_template('monitor/login.html')
            return HttpResponseBadRequest(template.render(context, request))


class LogoutView(View):
    """
    View class for the logout procedure
    """

    def get(self, request):
        """
        Handler method for GET requests
        :param request: request object
        :return: 302-Redirect response to the login page
        """
        logout(request)
        return HttpResponseRedirect(reverse('monitor:login'))
