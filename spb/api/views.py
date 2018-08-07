from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.authtoken.models import Token

from api.models import Pump, TransmittedTiming, ServiceTask
from monitor.decorators import user_is_authenticated


@method_decorator(user_is_authenticated, name='dispatch')
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
        if pump.owner != request.user:
            raise PermissionDenied()

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


@method_decorator(user_is_authenticated, name='dispatch')
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
        for e in TransmittedTiming.objects.filter(activeTime__gt=0, pump__owner=request.user):
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


@method_decorator(user_is_authenticated, name='dispatch')
class TransmittedTimingsView(View):
    def get(self, request, pid):
        """
        Handler method for GET requests

        :param request: Request object
        :param pid: Pump ID
        :return:  JSON dictionary with a list of all logged and transmitted pump timings for one specific pump
        """
        pump = get_object_or_404(Pump, pk=pid)
        if pump.owner != request.user:
            raise PermissionDenied()

        data = []
        for e in TransmittedTiming.objects.filter(activeTime__gt=0, pump=pump).order_by('timeStamp'):
            data.append({'timeStamp': e.timeStamp, 'active': e.activeTime, 'sleep': e.sleepTime})

        return JsonResponse({
            'xkey': 'timeStamp',
            'ykeys': ['active', 'sleep'],
            'labels': ['Active', 'Sleep'],
            'data': data,
        })


@method_decorator(user_is_authenticated, name='dispatch')
class ServiceTaskView(View):
    """
    View class for the deletion,retrieval and modification of a service task
    """

    def delete(self, request, tid):
        """
        Handler method for DELETE requests

        :param request: Request object
        :param tid: Task ID
        :return: Empty 200-OK response in case on success
        """
        task = get_object_or_404(ServiceTask, pk=tid)
        if task.pump.owner != request.user:
            raise PermissionDenied()
        task.delete()
        return HttpResponse()


@method_decorator(user_is_authenticated, name='dispatch')
class TokenView(View):
    """
    View class for the retrieval and update of an user authentication token
    """

    def get(self, request):
        """
        Handler method for GET requests

        :param request: Request object instance
        :return: Json response with the current token
        """

        return JsonResponse({
            'token': get_object_or_404(Token, user=request.user).key
        })

    def post(self, request):
        """
        Handler method for POST requests

        :param request: Request object instance
        :return: JSON response with new authentication response
        """
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass
        finally:
            return JsonResponse({
                'token': Token.objects.create(user=request.user).key
            })
