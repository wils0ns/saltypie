#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import json
import logging
import time
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.util.retry import Retry


class Salt(object):
    """Salt Rest API Handler"""

    CLIENT_LOCAL = 'local'
    CLIENT_RUNNER = 'runner'
    CLIENT_WHEEL = 'wheel'

    OUTPUT_RAW = 'raw'
    OUTPUT_JSON = 'json'
    OUTPUT_DICT = 'dict'

    def __init__(self, url, username=None, passwd=None, eauth='pam', trust_host=True):
        """
        Salt's Rest API handler

        Args:
            url (str): Salt API web server URL
            username (str): The username to be used to authenticate to the salt-api
            passwd (str): The password to be used to authenticate to the salt-api
            eauth (str): External authentication method.
            trust_host (bool): Whether or not to verify host certificates.
        """
        self.url = url
        self.username = username
        self.password = passwd
        self.eauth = eauth
        self.trust_host = trust_host
        self.token = None
        self.timeout = 60
        self.session = self._new_session()
        self.lookup_interval = 1
        self.max_retries_if_aborted = 3        

        self.log = logging.getLogger(__name__)

    def _new_session(self):
        """
        Creates a new requests Session

        Returns:
            request.Session
        """
        session = requests.Session()
        session.verify = not self.trust_host
        retries = Retry(total=3, backoff_factor=5)
        session.mount(self.url, HTTPAdapter(max_retries=retries))
        return session

    def get(self, path, headers=None, timeout=None):
        """
        Executes URL calls using the GET method

        Args:
            path (str): Path to append to the URL
            headers (dict): Extra headers to be passed to the GET call
            timeout (int): The amount of seconds to wait before the request times out

        Returns:
            requests.models.Response
        """
        if not self.session.verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        try:
            ret = self.session.get(
                url=urljoin(self.url, path),
                headers=headers,
                timeout=timeout or self.timeout
            )
            return ret
        except Exception as e:
            self.log.error(e)
            exit(1)

    def post(self, data, path='', headers=None, timeout=None):
        """
        Executes URL calls using the POST method

        Args:
            data (dict): The data to be passed to the POST call
            path (str): The path to be appended to the URL
            headers (dict): Extra headers to be passed to the POST call
            timeout (int): The amount of seconds to wait before the request times out

        Returns:
            requests.models.Response
        """
        if not self.session.verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        retries = self.max_retries_if_aborted or 1

        while True:
            try:
                ret = self.session.post(
                    url=urljoin(self.url, path),
                    data=data,
                    headers=headers,
                    timeout=timeout or self.timeout
                )
                return ret
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                self.log.error('Exception type: {}. Exception message: {}'.format(exc_type, exc_value))

                if 'RemoteDisconnected' in str(exc_value) and retries:
                    retries -= 1
                    self.log.warning(
                        'Execution failed because of connection abortion. Remaining retries: {} out of {}...'.format(
                            retries,
                            self.max_retries_if_aborted
                        )
                    )
                    time.sleep(5)
                else:
                    exit(1)

    def login(self, eauth=None):
        """
        Creates an authenticated session with a salt API server

        Args:
            eauth (str): External authentication method. 

        Returns:

        """
        eauth = eauth or self.eauth
        self.log.debug('Authenticating to salt-api using `{}` external authentication...'.format(eauth))
        data = {
            'username': self.username,
            'password': self.password,
            'eauth': eauth
        }

        try:
            r = self.post(path='login', data=data)
            self.token = r.json()['return'][0]['token']
            self.session.headers.update({'X-Auth-Token': self.token})
            self.log.debug('Authentication succeed.')
            return r.content
        except Exception:
            self.log.error('Error: Unable to connect to salt-api at `{}`. Return code: {}'.format(r.url, r.status_code))
            exit(1)

    def execute(self, fun, client=None, target=None, args=None, kwargs=None, pillar=None, async=False, async_wait=False,
                output='dict', returner=None):
        """
        Executes a function using the salt API.

        Args:
            fun (str): Name of the function to be executed
            client (str): Type of client to use (local, runner or wheel).
                          If not specified, the `local` client will be used.
            target (str): The minions that should execute this function.
                          If the client is not set to `local`, this parameter will be ignored.
            args (list): List of arguments to be passed to the function.
            kwargs (dict): Dictionary of arguments to be passed to the function.
            pillar (dict): Dictionary of pillar values to be passed to the function. Example: pillar={'sleep': 30}
            async (bool): Whether or not to execute the function asynchronously.
                          If set to `True`, it will return the job ID.
                          If the client is set to `wheel`, this parameter wil be ignored.
            async_wait (bool): If this parameter is set to `True`, it will use async clients, just like the `async`
                               parameter would, but instead of returning the job ID, it will use it to keep pulling
                               the job result until it is completed. It is basically the same as passing `async=True`
                               and calling `Salt.lookup_job` with `until_complete=True`. Crazy right? But super useful
                               for long run functions that you would like to wait for the return, but don't want to
                               be vulnerable to timeouts (You're welcome.).
            output (str): The output format of this method (See output constants specified in this class).
            returner (str): Which salt returner to be passed to the function.

        Returns:
            str, dict: Depends on the format passed to the `output` parameter.
        """

        if not self.token:
            self.login()

        client = client or Salt.CLIENT_LOCAL

        if async or async_wait and not (client == Salt.CLIENT_WHEEL):
            client += '_async'

        data = {
            'client': client,
            'fun': fun,
        }

        if target:
            data.update({'tgt': target})
        if pillar:
            args = args or []
            args.append('pillar={}'.format(json.dumps(pillar)))
        if args:
            data.update({'arg': args})
        if kwargs:
            if client == Salt.CLIENT_LOCAL:
                data.update({'kwarg': kwargs})
            else:
                data.update(**kwargs)

        if returner:
            data.update({'ret': returner})

        self.log.debug('Executing salt command: {}'.format(data))
        ret = self.post(data)
        if async_wait:
            return self.lookup_job(json.loads(ret.content)['return'][0]['jid'], until_complete=True, output=output)
        elif async:
            return json.loads(ret.content)
        elif output == Salt.OUTPUT_DICT:
            return json.loads(ret.content)
        elif output == Salt.OUTPUT_RAW:
            return ret.content
        elif output == Salt.OUTPUT_JSON:
            return str(ret.content)

    def lookup_job(self, jid, until_complete=False, interval=None, output='dict'):
        """
        Retrieves information about a saltstack job.

        Args:
            jid (int): The job ID.
            until_complete (bool): Whether or not to keep pulling the job until it is completed.
            interval (int): Time interval (in seconds) to wait in between checks. If not specified, defaults will be used.
                You can also set the global lookup interval using `self.lookup_interval`.
            output (str): The output format of this method (See output constants specified in this class).
        Returns:
            dict: a dictionary containing the job results
        """
        if not self.token:
            self.login()

        ret = self.execute(client=Salt.CLIENT_RUNNER, fun='jobs.lookup_jid', kwargs={'jid': jid}, output=output)

        if until_complete:
            while ret['return'][0] == {}:
                time.sleep(interval or self.lookup_interval)
                ret = self.lookup_job(jid)

        return ret

    def highstate(self, target, output='dict'):
        """
        Runs highstate on the target minion

        Args:
            target (str): The minion to run the highstate
            output (str): The output format of this method (See output constants specified in this class).
        Returns:
            str, dict: Depends on the format passed to the `output` parameter.
        """
        return self.execute(fun='state.apply', target=target, async_wait=True, output=output)

    def versions(self):
        """
        Returns the versions of salt running on master and its minions

        Returns:
            dict
        """
        ret = self.execute(fun='manage.versions', client=Salt.CLIENT_RUNNER)['return'][0]
        v = {
            'master': ret['Master'],
            'minions': {}
        }

        if 'Up to date' in ret.keys():
            v['minions'].update(ret['Up to date'])

        if 'Minion requires update' in ret.keys():
            v['minions'].update(ret['Minion requires update'])
        return v
