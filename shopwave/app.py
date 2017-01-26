#! -*- coding: utf-8 -*-

import logging
import falcon
import json
from shopwave import Credentials, Scope

from settings import (OAUTH_BASE_URL, TOKEN_URI, API_BASE_URL, CLIENT_ID,
                      CLIENT_SECRET, AUTH_URI, ACCESS_TYPE, REDIRECT_URI,
                      RESPONSE_TYPE)


class AuthAPI:
    scope = Scope()
    cred = Credentials(scope=scope)

    def on_get(self, requ, resp):
        cred = self.cred
        if 'login' in requ.params.keys() and requ.params['login'] == 'true':
            # redirect to Shopwave auth uri.
            raise falcon.HTTPFound(cred.get_auth_app_uri())
        if 'code' in requ.params.keys():
            auth_code = requ.params['code']
            cred.verify(auth_code)

            logging.info('Got creds.')
 
api = falcon.API()
api.add_route('/api', AuthAPI())

