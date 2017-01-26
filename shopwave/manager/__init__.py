#! -*- coding: utf-8 -*-



from shopwave.manager.base import (
    GenericManager, Report_BasketManager)
from shopwave.manager import base as base_manager


def get_manager_class(name):
    if hasattr(base_manager, "{0}Manager".format(name)):
        ManagerClass = getattr(base_manager, "{0}Manager".format(name))
    else:
        ManagerClass = GenericManager
    return ManagerClass

