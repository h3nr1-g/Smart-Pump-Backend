from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseGone
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.views import View
from api.models import Pump, ServiceTask
from monitor.forms import PumpModelForm
from monitor.tables import PumpTable


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
            'table': PumpTable(Pump.objects.all()),
            'title': 'Pump Overview'
        }
        return render(request, 'monitor/overview.html', context)


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
        form = PumpModelForm(instance=pump)
        context = {
            'title': 'Pump {}'.format(pump),
            'form': form,
            'pump': pump,
            'tasks': ServiceTask.objects.filter(pump=pump)
        }
        return render(request, 'monitor/pump_details.html', context)

    def delete(self, request, pid):
        """
        Handler method for DELETE requests

        :param request: Request object
        :param pid: Pump ID
        :return: Empty 200-OK response on success
        """
        get_object_or_404(Pump, pk=pid).delete()
        return HttpResponse()

    def post(self, request, pid):
        """
        Handler method for POST requests

        :param request: Request object
        :param pid: Pump ID
        :return: HTML page with updated information
        """
        pump = get_object_or_404(Pump, pk=pid)
        form = PumpModelForm(request.POST, instance=pump)
        context = {
            'title': 'Pump - {}'.format(pump),
            'form': form,
            'pump': pump,
            'tasks': ServiceTask.objects.filter(pump=pump)
        }
        if form.is_valid():
            context['success_notification'] = 'Changes saved.'
            form.save()
            return render(request, 'monitor/pump_details.html', context)

        template = loader.get_template('monitor/pump_details.html')
        return HttpResponseBadRequest(template.render(context, request))


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
