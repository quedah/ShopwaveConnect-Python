#! -*- coding: utf-8 -*-

import requests
import redis
import logging

from requests.exceptions import HTTPError

# shopwave

from settings import (OAUTH_BASE_URL, TOKEN_URI, API_BASE_URL, CLIENT_ID,
                      CLIENT_SECRET, AUTH_URI, REDIRECT_URI, AVAILABLE_SCOPES, 
                      ACCESS_TYPE, RESPONSE_TYPE, REDIS_STORE)

class Scope(object):
    def __init__(self, active_scopes=None):
        """
        Parameters
        ----------
        scope : iterable
            Scopes to select for authorisation in authentication process. See
            AVAILABLE_SCOPES for possible values.
        """

        if not active_scopes:
            for scope in AVAILABLE_SCOPES:
                setattr(self, scope, True)
        else:
            for scope in AVAILABLE_SCOPES:
                if scope in active_scopes:
                    setattr(self, scope, True)
                else:
                    setattr(self, scope, False)

    def __str__(self):
        return ",".join(self.list())

    def list(self):
        return [scope for scope in AVAILABLE_SCOPES if getattr(self, scope)]

class Credentials(object):
    # TODO: Can I rely on that client_id will not change??
    """

    """
    def __init__(self, scope=None, authorization_code=None):
        """
        Parameters
        ----------
        scope : Scope
        authorization_code : string
            Authorization code for obtaining access token.
        """
        self.db = redis.StrictRedis(host=REDIS_STORE['host'], 
                                    port=REDIS_STORE['port'])

        db_keys_raw = ['access_token', 'refresh_token', 'token_type', 'auth_code']
        self._db_keys = {key: CLIENT_ID + ":" + key for key in db_keys_raw}

        if scope:       self.scope = scope
        else:           self.scope = Scope()

        if authorization_code:  
            self.verify(authorization_code)
            #self.db.set(self._db_keys['auth_code'], authorization_code)
        self._get_token()

    def verify(self, authorization_code):
        self.db.set(self._db_keys['auth_code'], authorization_code)

    def delete(self):
        self.db.delete(self._db_keys['access_token'])
        self.db.delete(self._db_keys['refresh_token'])
        self.db.delete(self._db_keys['token_type'])

    def _db_get(self, key):
        """
        Fetch value from redis DB and convert value from bytes to string.
        """
        value = self.db.get(self._db_keys[key])
        if value:   return value.decode()
        else:       return None

    def _get_token(self):
        """
        Tries multiple approaches to get a valid access token:
            1. Checks DB for token
            2. Checks DB for refresh token to request new access token
            3. Checks DB for authorization code to request new access and
               refresh token.
        """
        self.access_token = self._db_get('access_token')
        self.refresh_token = self._db_get('refresh_token')
        if not self.access_token:    
            print("NO DB ACCESS_TOKEN, TRYING TO USE REFRESH-TOKEN.")
            self._refresh_token_call()
        else:
            print("RETRIEVED ACCESS-TOKEN FROM DB.")

        self.token_type = self._db_get('token_type')

        return self.access_token

    def __save(self):
        access_token = getattr(self, 'access_token', None)
        expires_in = getattr(self, 'expires_in', None)
        token_type = getattr(self, 'token_type', None)
        if access_token and expires_in and token_type:
            self.db.setex(self._db_keys['access_token'], 
                          expires_in,
                          access_token)
            self.db.setex(self._db_keys['token_type'], 
                          expires_in,
                          token_type)
        refresh_token = getattr(self, 'refresh_token', None)
        if refresh_token:
            self.db.set(self._db_keys['refresh_token'], refresh_token)

    def _refresh_token_call(self):
        """
        Request new access token and using refresh token.
        """
        refresh_token = self.db.get(self._db_keys['refresh_token'])
        if not refresh_token:
            self._make_token_call()
        else:
            post_data = {
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            keys = ['access_token', 'token_type', 'expires_in']
            return self.__generic_token_call(keys, post_data)

    def _make_token_call(self, authorization_code=None):
        """
        Request new access token and refresh token using auth. code.
        """
        if not authorization_code:
            authorization_code = self.db.get(self._db_keys['auth_code'])
        post_data = {
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        keys = ['access_token', 'refresh_token', 'token_type', 'expires_in']
        try:
            resp = self.__generic_token_call(keys, post_data)
            return resp
        except HTTPError:
            return None

    def __generic_token_call(self, keys, post_data):
        """
        Parameters
        ----------
        keys : iterable, str
            key values to extract from response body. 
        post_data : dict
            Data to submit in POST request.
        """
        post_data.update({
            'access_type': ACCESS_TYPE,
            'client_id': CLIENT_ID, 
            'redirect_uri': REDIRECT_URI,
            'scope': str(self.scope),
            'client_secret': CLIENT_SECRET,
        })
        resp = requests.post(TOKEN_URI, post_data)
        print(resp.content)
        data = resp.json()

        if resp.status_code == 200:
            for k in keys: setattr(self, k, data[k])

        #elif all(map(lambda k: k in data.keys())):
        #    # Unexpected status code, but all requested keys in response body.
        #    for k in keys: setattr(self, k, data[k])
        #    print("[HTTP{0}] TOKEN CALL".format(resp.status_code))
        elif resp.status_code == 401:
            # Invalid refresh token. Make completely new token call.
            auth_code = self.db.get(self._db_keys['auth_code'])
            if auth_code:   
                # TODO loop-danger!!!
                self._make_token_call(auth_code)
            else:           
                if 'grant_type' in post_data.keys():
                    errmsg =  'Invalid {0}!'.format(post_data['grant_type'])
                else:
                    errmsg =  'Invalid authentication!'
                raise HTTPError(401, errmsg)
        else:
            if 'error' in data.keys():  
                message = data['error']
            else:                       
                message = "Undefined error, could not fetch token!"
            raise HTTPError(resp.status_code, message)

        self.__save()
        return resp

    def get_auth_app_uri(self):
        return OAUTH_BASE_URL + AUTH_URI +\
                   "?access_type="  + ACCESS_TYPE +\
                   "&redirect_uri=" + REDIRECT_URI +\
                   "&client_id="    + CLIENT_ID +\
                   "&scope="        + str(Scope()) + \
                   "&response_type=" + RESPONSE_TYPE
        # FIX SCOPE!!!

