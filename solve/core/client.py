import platform
import requests
from requests.auth import AuthBase

from solve import __version__
from solve.core import API_HOST
from solve.core.solvelog import solvelog
from solve.core.credentials import get_api_key


class SolveAPIError(BaseException):
    pass


class SolveTokenAuth(AuthBase):
    """Custom auth handler for Solve API token authentication"""
    def __init__(self, token=None):
        self.token = token or get_api_key()

    def __call__(self, r):
        if self.token:
            r.headers['Authorization'] = 'Token %s' % self.token
        return r


class SolveClient(object):
    def __init__(self, use_ssl=False):
        # self.session = requests.Session()
        self.proto = ('http', 'https')[use_ssl]
        self.api_host = '%s://%s' % (self.proto, API_HOST)
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Solve Client %s [Python %s/%s]' % (
                __version__, platform.python_implementation(), platform.python_version()
            )
        }

    def _request(self, method, path, data={}, params={}):
        if not path.startswith('/'):
            path = '/%s' % path

        solvelog.debug('API %s Request: %s' % (method.upper(), self.api_host + path))
        resp = requests.request(method=method, url=self.api_host + path,
                                params=params, data=data,
                                auth=SolveTokenAuth(),
                                stream=False, verify=True)

        solvelog.debug('API Response: %d' % resp.status_code)
        if resp.status_code not in range(200, 210):
            raise SolveAPIError(self._get_error_message(resp))

        return resp.json()

    def _get_error_message(self, response):
        try:
            body = response.json()
        except:
            solvelog.error('API Error: no JSON response.')
            return 'No response from server.'
        else:
            if u'non_field_errors' in body:
                return '\n'.join(body['non_field_errors'])
            elif u'detail' in body:
                return body['detail']
            else:
                solvelog.error('API Error response: ' + str(body))
                return ''

    def post_login(self, email, password):
        """Get a auth token for the given user credentials"""
        data = {
            'email': email,
            'password': password
        }

        return self._request('POST', '/auth/token/', data=data)

    def post_signup(self, email, password):
        data = {
            'email': email,
            'password': password
        }

        return self._request('POST', '/user/signup/', data=data)

    def get_current_user(self):
        return self._request('GET', '/user/current/')

    def post_install_report(self):
        data = {
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'platform': platform.platform(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'pyexe_build': platform.architecture()[0]
        }
        self._request('POST', '/report/install', data=data)
