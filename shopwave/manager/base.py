#! -*- coding: utf-8 -*-

import requests
import json
from settings import __dict__ as settings
from settings import OBJECT_LIST, API_BASE_URL, X_ACCEPT_VERSION, USER_AGENT

from shopwave.utils import ShopwaveDatetime, ONE_DAY
from shopwave import models
from shopwave.models import MODEL_LIST
from shopwave.exceptions import (
    ShopwaveBadRequest, ShopwaveUnauthorized, ShopwaveForbidden,
    ShopwaveNotFound, ShopwaveExceptionUnknown)


class GenericManager(object):
    DECORATED_METHODS = (
        'all',
        'get'
    )

    def __init__(self, name, credentials):
        self.credentials = credentials
        self.name = name
        self.base_url = API_BASE_URL 
        self.headers = {
            'Authorization': 'Bearer {token}'.format(token=credentials.access_token),
            'x-accept-version': X_ACCEPT_VERSION,
            'accept': 'application/json'
        }

        for method_name in self.DECORATED_METHODS:
            method = getattr(self, '_%s' % method_name)
            setattr(self, method_name, self._get_data(method))

    def _post_data(self):
        raise NotImplementedError
        if method.upper() == 'POST':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'


    def _get_data(self, func):
        """ Decorator for DECORATED_METHODS. Decorated method must return 
        uri, params, method, body, headers.
        """
        def wrapper(*args, **kwargs):
            timeout = kwargs.pop('timeout', None)
            return_format = kwargs.pop('return_format', None)
            uri, params, method, body, headers = func(*args, **kwargs)
            if headers is None:     headers = {}
            headers.update(self.headers)

            # Set a user-agent so Xero knows the traffic is coming from pyxero
            # or individual user/partner
            headers['User-Agent'] = USER_AGENT

            response = getattr(requests, method)(
                    uri, data=body, headers=headers,
                    params=params, timeout=timeout)


            if response.status_code == 200:
                # If we haven't got XML or JSON, assume we're being returned a binary file
                if not response.headers['content-type'].startswith('application/json'):
                    return response.content

                return self._parse_api_response(response, self.name,
                                                return_format=return_format)

            elif response.status_code == 400:
                raise ShopwaveBadRequest(response)

            elif response.status_code == 401:
                #return response
                raise ShopwaveUnauthorized(response)

            elif response.status_code == 403:
                raise ShopwaveForbidden(response)

            elif response.status_code == 404:
                raise ShopwaveNotFound(response)

            elif response.status_code == 500:
                raise ShopwaveInternalError(response)

            else:
                raise ShopwaveExceptionUnknown(response)

        return wrapper


    def _parse_api_response(self, response, resource_name, return_format=None):
        data = json.loads(response.text)
        assert response.status_code == 200, "Expected the API to return HTTP200\
            code, but received {0}".format(response.status_code)

        # Don't need api part of response here
        data.pop('api', None)

        if return_format is not None and return_format.upper() == 'JSON':
            return data
        else:
            return self._parse_json(data)

    def _parse_json(self, json_data):
        """
        NOT NAMED CORRECTLY - INCONVENIENT TO PASS JSON INSTEAD OF DICT!!
        """
        result = dict()
        for obj_name in list(json_data):
            data = json_data[obj_name]
            matching = None
            
            # Finding matching model class
            obj1 = obj_name[:-1]
            while len(obj1) > 1:
                n = len(obj1)
                check = lambda x: (x[:n].lower()==obj1.lower())
                matching = [obj2 for obj2 in MODEL_LIST if check(obj2)]
                if matching: break
                obj1 = obj1[:-1]

            # Parsing data
            obj_list = list()
            while matching: 
                try:
                    ModelClass = getattr(models, matching.pop())
                    for item_id in list(data):
                        obj_list.append(ModelClass(data=data[item_id]))
                    break
                except TypeError as e:
                    raise e
                    # Continue to next class in list 'matching'. If no match,
                    # ValueError will be raised at end.
                    pass

            if obj_list: 
                result[obj_name] = obj_list
            else:
                raise ValueError("Failed to parse the provided JSON data. "+\
                                 "No matching object found.")
        if len(obj_list) == 1:
            return list(result.values())
        else:
            return result

    def _all(self, **kwargs):
        """
        Returns
        -------
        uri, params, method, body, headers for http request.
        """
        uri = self.base_url + self.name.lower().replace('_', '/')
        return uri, {}, 'get', None, kwargs.get('headers', None)

    def _get(self, ids, **kwargs):
        """
        Parameters
        ----------
        ids : string, comma separated values

        Returns
        -------
        uri, params, method, body, headers for http request.
        """
        uri = self.base_url + self.name.lower().replace('_', '/')
        headers = kwargs.get('headers', {})
        headers['%sIds' % self.name.lower()] = ids
        return uri, {}, 'get', None, headers


class Report_BasketManager(GenericManager):
    def __init__(self, *args, **kwargs):
        super(Report_BasketManager, self).__init__(*args, **kwargs)

    def _all(self, from_date=None, to_date=None):
        """
        If *from* date not specified, will default to 1 day timeframe. If *to* date
        not specified will set to now.

        Parameters
        ---------
        """
        if from_date is None and to_date is None:
            to_date = ShopwaveDatetime.now()
            from_date = ShopwaveDatetime.now() - ONE_DAY
        elif to_date is None:
            to_date = ShopwaveDatetime()
            from_date = ShopwaveDatetime(from_date)
        elif from_date is None:
            to_date = ShopwaveDatetime(to_date)
            from_date = to_date - ONE_DAY

        # Make sure date/time is in required format
        from_date = ShopwaveDatetime(from_date).to_str()
        to_date = ShopwaveDatetime(to_date).to_str()

        headers = {
            'to':       to_date,
            'from':     from_date 
        }

        return super(Report_BasketManager, self)._all(headers=headers)

