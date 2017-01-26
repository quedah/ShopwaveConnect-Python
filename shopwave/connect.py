#! -*- coding: utf-8 -*-

import requests

from settings import (API_BASE_URL)
from urllib.parse import urlencode
import json

from shopwave import manager
from shopwave.settings import OBJECT_LIST


class Shopwave(object):

    def __init__(self, credentials):
        self.OBJECT_LIST = OBJECT_LIST
        for name in self.OBJECT_LIST:
            ManagerClass = manager.get_manager_class(name)
            setattr(self, name.lower(), ManagerClass(name, credentials))



class BasketTransaction(object):
    pass
