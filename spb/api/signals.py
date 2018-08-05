from django.db.models.signals import pre_delete
from django.dispatch import receiver
from api.models import ServiceTask


@receiver(pre_delete, sender=ServiceTask)
def update_service_status(**kwargs):
    """
    Method gets called before an instance of ServiceTask class gets deleted, method checks if the submitted instance
    is the last service task for this pump and sets pump.needsService to False if so

    :param sender:
    :param kwargs:
    :return: None
    """
    if len(ServiceTask.objects.filter(pump=kwargs['instance'].pump)) < 2:
        kwargs['instance'].pump.needsService = False
        kwargs['instance'].pump.save()
