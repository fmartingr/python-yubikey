#!/usr/bin/env python
import requests
import string
from random import choice


class YubicoWS(object):
    register_ws = 'https://upgrade.yubico.com/getapikey/?format=json'
    _api_ws = 'http://%s/wsapi/2.0/'
    api_ws = None
    
    _servers = [
        'api.yubico.com',
        'api2.yubico.com',
        'api3.yubico.com',
        'api4.yubico.com',
        'api5.yubico.com',
    ]
    
    _errors = {
        'BAD_OTP': 'The OTP is invalid format.',
        'REPLAYED_OTP': 'The OTP has already been seen by the service.',
        'BAD_SIGNATURE': 'The HMAC signature verification failed.',
        'MISSING_PARAMETER': 'The request lacks a parameter.',
        'NO_SUCH_CLIENT': 'The request id does not exist.',
        'OPERATION_NOT_ALLOWED': 'The request id is not allowed to verify OTPs.',
        'BACKEND_ERROR': 'Unexpected error in our server. Please contact us if you see this error.',
        'NOT_ENOUGH_ANSWERS': 'Server could not get requested number of syncs during before timeout',
        'REPLAYED_REQUEST': 'Server has seen the OTP/Nonce combination before',
    }
    
    def __init__(self):
        self.select_random_server()

    def select_random_server(self):
        "Select random API Server"
        self.api_ws = self._api_ws % choice(self._servers)

    def register_api_key(self, email, otp):
        data = {
            'email': email,
            'otp': str.lower(otp)
        }
        response = requests.post(self.register_ws, data)
        ws_response = response.json()
        if not ws_response['status']:
            raise WSError(ws_response['error'])
            
        return ws_response
        
    def verify(self, yubikey_id, otp):
        endpoint = 'verify'
        url = self.api_ws + endpoint
        
        # Check otp format
        if not (len(otp) > 32 and len(otp) < 48):
            raise OTPIncorrectFormat()
            
        nonce = self.generate_nonce()
        
        data = {
            'id': int(yubikey_id),
            'otp': str.lower(otp),
            'nonce': nonce
        }
        
        response = requests.get(url, params=data)
        
        ws_response = self.parse_ws_response(response.text)
        print(ws_response)
        if ws_response['status'] == 'OK':
            # Check if response is valid
            if not (ws_response['nonce'] == nonce \
                and ws_response['otp'] != otp \
                and True):
                raise WSInvalidResponse()
        else:
            raise WSError(self._errors[ws_response['status']])
        
        return ws_response

    def parse_ws_response(self, text):
        data = {}
        for line in text.strip().split('\n'):
            key, value = line.split('=', 1)
            data[key] = value
        return data

    def generate_nonce(self):
        chars = string.ascii_lowercase + string.digits
        return ''.join(choice(chars) for x in range(40))


class Yubikey(object):
    id = None
    key = None
    prefix = None
    
    _last_result = False
    
    def __init__(self, yubikey_id=None):
        self.ws = YubicoWS()
        if yubikey_id:
            self.id = yubikey_id

    def register(self, email, otp):
        result = False
        if not self.id:
            credentials = self.ws.register_api_key(email, otp)
            if credentials['status']:
                self.id = credentials['id']
                self.key = credentials['key']
                result = True
                
        return result
        
    def verify(self, otp):
        result = False
        if self.id:
            self.get_prefix(otp)
            result = self.ws.verify(self.id, otp)
            if result == 'OK':
                result = True
                
        self._last_result = result
        return result
        
    def get_prefix(self, otp):
        if len(otp) > 32:
            self.prefix = str.lower(otp[:-32])
        

class WSError(Exception):
    def __init__(self, message=None):
        self.msg = "Web Service responded with an error: %s" % message
    
    def __str__(self):
        return repr(self.msg)
        

class WSInvalidResponse(Exception):
    msg = 'Response from the server is invalid'


class WSResponseError(Exception):
    def __str__(self):
        return repr(self.msg)

class OTPIncorrectFormat(Exception):
    pass
