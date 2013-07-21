#!/usr/bin/env python
import string
from random import choice
import base64
from hashlib import sha1
import hmac
import requests


class YubicoWS(object):
    """
    Yubico Web Service class that interacts with the Yubico API
    """

    register_ws = 'https://upgrade.yubico.com/getapikey/?format=json'
    api_ws = None

    _protocol = 'https'

    _servers = [
        'api.yubico.com',
        'api2.yubico.com',
        'api3.yubico.com',
        'api4.yubico.com',
        'api5.yubico.com',
    ]
    _server = None

    _api_ws = '%s://%s/wsapi/2.0/'

    _errors = {
        'BAD_OTP': 'The OTP is invalid format.',
        'REPLAYED_OTP': 'The OTP has already been seen by the service.',
        'BAD_SIGNATURE': 'The HMAC signature verification failed.',
        'MISSING_PARAMETER': 'The request lacks a parameter.',
        'NO_SUCH_CLIENT': 'The request id does not exist.',
        'OPERATION_NOT_ALLOWED': 'The request id is not allowed '
                                 'to verify OTPs.',
        'BACKEND_ERROR': 'Unexpected error in our server. Please contact '
                         'us if you see this error.',
        # 2.0
        'NOT_ENOUGH_ANSWERS': 'Server could not get requested number of syncs '
                              'during before timeout',
        'REPLAYED_REQUEST': 'Server has seen the OTP/Nonce combination before',
    }

    def __init__(self, **kwargs):
        self._protocol = kwargs.get('protocol', self._protocol)
        self._server = kwargs.get('server', None)
        self.select_server()

    def select_server(self):
        "Select server if provided, otherwise uses one from the list"
        if self._server and self._server in self._servers:
            self.api_ws = self._api_ws % (self._protocol, self._server)
        else:
            self.api_ws = self._api_ws % (
                self._protocol,
                choice(self._servers)
            )

    def register_api_key(self, email, otp):
        "Registers an API Key with the servers"
        data = {
            'email': email,
            'otp': str.lower(otp)
        }
        response = requests.post(self.register_ws, data)
        ws_response = response.json()
        if not ws_response['status']:
            raise YubicoWSError(ws_response['error'])

        return ws_response

    def verify(self, yubikey_id, otp, key=None):
        "Verifies the provided OTP with the server"
        endpoint = 'verify'
        url = self.api_ws + endpoint

        # Check otp format
        if not (len(otp) > 32 and len(otp) < 48):
            raise OTPIncorrectFormat()

        nonce = self.generate_nonce()

        data = {
            'id': str(yubikey_id),
            'otp': str.lower(otp),
            'nonce': nonce
        }

        # Use API key for signing the message if key is provided
        if key:
            data['h'] = self.sign(data, key)

        response = requests.get(url, params=data)

        ws_response = self.parse_ws_response(response.text)

        if ws_response['status'] == 'OK':
            # Check if response is valid
            if not (ws_response['nonce'] == data['nonce']
                    and ws_response['otp'] == otp):
                raise YubicoWSInvalidResponse()

            if key:
                signature = self.sign(ws_response, key)

                if ws_response['h'] != signature:
                    raise YubicoWSResponseBadSignature(
                        "The signature sent by the server is invalid"
                    )

        else:
            raise YubicoWSError(self._errors[ws_response['status']])

        return ws_response

    def sign(self, data, key):
        "Signs the message with the provided key"
        # Sort k=v dict
        params = []

        for k in sorted(data.keys()):
            if k != 'h':  # Just in case
                key_value = "%s=%s" % (k, data[k])
                params.append(key_value)

        # Join as urlparams
        parameters = '&'.join(params)

        # hmac-sha1
        hashed_string = hmac.new(
            base64.b64decode(key),
            parameters,
            sha1
        ).digest()

        # base64 encode
        signature = base64.b64encode(hashed_string)

        return signature

    def parse_ws_response(self, text):
        "Parses the API key=value response into a dict"
        data = {}
        for line in text.split():
            key, value = line.split('=', 1)
            data[key.strip()] = value.strip()
        return data

    def generate_nonce(self):
        "Generates a random string"
        chars = string.ascii_lowercase + string.digits
        return ''.join(choice(chars) for x in range(40))


class Yubikey(object):
    """
    Yubikey object wrapper
    """

    id = None
    key = None
    prefix = None

    _last_result = False

    def __init__(self, yubikey_id=None, key=None, **kwargs):
        self.ws = YubicoWS(**kwargs)
        if yubikey_id:
            self.id = yubikey_id
        if key:
            self.key = key

    def register(self, email, otp):
        "Registers this yubikey"
        result = False
        if not self.id:
            credentials = self.ws.register_api_key(email, otp)
            if credentials['status']:
                self.id = credentials['id']
                self.key = credentials['key']
                result = True

        return result

    def verify(self, otp):
        "Verify an OTP to check if its valid"
        result = False
        if self.id:
            self.get_prefix(otp)
            try:
                self.ws.verify(self.id, otp, key=self.key)
                result = True
            except (YubicoWSResponseBadSignature, YubicoWSError):
                result = False

        self._last_result = result
        return result

    def get_prefix(self, otp):
        "Get prefix from an OTP if present"
        if len(otp) > 32:
            self.prefix = str.lower(otp[:-32])


###
# Custom exceptions
###
class YubicoWSError(Exception):
    "Web service error. Defined by yubico documentation."
    def __init__(self, message=None):
        self.msg = "Web Service responded with an error: %s" % message

    def __str__(self):
        return repr(self.msg)


class YubicoWSInvalidResponse(Exception):
    "Exception if the web service answers without same otp/nonce parameters"
    msg = 'Response from the server is invalid'


class YubicoWSResponseBadSignature(Exception):
    "Exception if the web service answers with a invalid signature"
    pass


class OTPIncorrectFormat(Exception):
    "Exception raised if the OTP provided is incorrect"
    pass
