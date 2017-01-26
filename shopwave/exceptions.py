#! -*- coding: utf-8 -*-

import json


class ShopwaveException(Exception):
    def __init__(self, response, msg=None):
        self.response = response
        if not msg:
            if response.headers['content-type'].startswith('application/json'):
                data = response.json()
                try:
                    errs = data['api']['message']['errors']
                    msg = ''
                    for e_id in errs.keys():
                        msg += "[ERROR {id}] {title}. ".format(**errs[e_id])
                        if 'details' in errs[e_id].keys():
                            msg += "{details}".format(**errs[e_id])
                            if msg[-1] == '.':  msg += ' '
                            else:               msg += '. '
                        if 'moreInfo' in errs[e_id].keys():
                            msg += "{moreInfo}".format(**errs[e_id])
                            if msg[-1] == '.':  msg += ' '
                            else:               msg += '. '
                except KeyError:
                    msg = "HTTP {0} ERROR".format(response.status_code)

            else:
                msg = "HTTP {0} ERROR".format(response.status_code)
        super(ShopwaveException, self).__init__(msg)

class ShopwaveBadRequest(ShopwaveException):
    # HTTP 400: Bad Request
    def __init__(self, response):
        super(ShopwaveBadRequest, self).__init__(response)

class ShopwaveUnauthorized(ShopwaveException):
    # HTTP 401: Unauthorized
    def __init__(self, response):
        super(ShopwaveUnauthorized, self).__init__(response)

class ShopwaveForbidden(ShopwaveException):
    # HTTP 403: Forbidden
    def __init__(self, response):
        super(ShopwaveForbidden, self).__init__(response)

class ShopwaveNotFound(ShopwaveException):
    # HTTP 404: Not Found
    def __init__(self, response):
        super(ShopwaveNotFound, self).__init__(response)

class ShopwaveInternalError(ShopwaveException):
    # HTTP 500: Internal Error
    def __init__(self, response):
        super(ShopwaveInternalError, self).__init__(response)

class ShopwaveExceptionUnknown(ShopwaveException):
    def __init__(self, response):
        super(ShopwaveExceptionUnknown, self).__init__(response)
