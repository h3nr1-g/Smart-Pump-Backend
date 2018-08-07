from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_token(**kwargs):
    """
    Method creates for all registered users an authentication token which can be used for HTTP requests

    :param sender:
    :param kwargs:
    :return: None
    """
    if len(Token.objects.filter(user=kwargs['instance'])) < 1:
        Token.objects.create(user=kwargs['instance'])
