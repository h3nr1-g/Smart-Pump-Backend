from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from api.models import Pump, TransmittedTiming, ServiceTask


class TimingsView(View):
    """
    View class is used for the activation of a pump, pumps controller fetches data from this view on a regular base
    """

    def get(self, request, pid):
        """
        Handler method for GET requests

        :param request: Request object
        :param pid: id of the pump
        :return: JSON dictionary with values for stand by and working time
        """
        pump = get_object_or_404(Pump, pk=pid)
        active = pump.activeTime if pump.active and not pump.needsService else 0
        sleep = pump.sleepTime
        if active > 0:
            pump.update_capacity(active)
            pump.health_check()
        TransmittedTiming.objects.create(activeTime=active, sleepTime=sleep, pump=pump)

        return JsonResponse({
            'active': active,
            'sleep': int(sleep),
        })


class TimingAggregatorView(View):
    """
    View class for the aggregation of the activities by all pumps
    """

    def get(self, request):
        """
        Handler method for GET requests

        :param request: Request object
        :return:  JSON dictionary with a list of all logged and transmitted pump timings
        """
        data = []
        for e in TransmittedTiming.objects.filter(activeTime__gt=0):
            data.append({
                'timeStamp': e.timeStamp,
                e.pump.name.replace(' ', '_'): e.activeTime
            })
        pumps = Pump.objects.all()

        return JsonResponse({
            'xkey': 'timeStamp',
            'labels': [p.name for p in pumps],
            'ykeys': [p.name.replace(' ', '_') for p in pumps],
            'data': data
        })


class TransmittedTimingsView(View):
    def get(self, request, pid):
        """
        Handler method for GET requests

        :param request: Request object
        :param pid: Pump ID
        :return:  JSON dictionary with a list of all logged and transmitted pump timings for one specific pump
        """
        pump = get_object_or_404(Pump, pk=pid)
        data = []
        for e in TransmittedTiming.objects.filter(activeTime__gt=0, pump=pump).order_by('timeStamp'):
            data.append({'timeStamp': e.timeStamp, 'active': e.activeTime, 'sleep': e.sleepTime})

        return JsonResponse({
            'xkey': 'timeStamp',
            'ykeys': ['active', 'sleep'],
            'labels': ['Active', 'Sleep'],
            'data': data,
        })


class ServiceTaskView(View):
    """
    View class for the deletion,retrieval and modificaton of a service task
    """

    def delete(self, request, tid):
        """
        Handler method for DELETE requests

        :param request: Request object
        :param tid: Task ID
        :return: Empty 200-OK response in case on success
        """
        get_object_or_404(ServiceTask, pk=tid).delete()
        return HttpResponse()
