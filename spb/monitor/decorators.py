# -*- coding: utf-8 -*-

"""@package docstring
Module for the definition of decorators
author: Henry Glueck
"""

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def check_authentication(user):
    """
    Simple decorator method, that checks if the user is authenticated
    :param user: user object
    :return: True if the user is authenticated else method raises a PermissionDenied exception
    """
    if not user.is_authenticated:
        raise PermissionDenied()
    else:
        return True


user_is_authenticated = user_passes_test(check_authentication)
