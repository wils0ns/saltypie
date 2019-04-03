#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=E1101
"""Saltstack REST API handler"""

from __future__ import print_function

import sys
import json
import logging
import time
from datetime import datetime

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.util.retry import Retry


from saltypie.exceptions import SaltConnectionError, SaltAuthenticationError, SaltReturnParseError


class Salt(object):
    """
    Salt's Rest API handler

    Args:
        url (str): Salt API web server URL
        username (str): The username to be used to authenticate to the salt-api
        passwd (str): The password to be used to authenticate to the salt-api
        eauth (str): External authentication method.
        trust_host (bool): Whether or not to verify host certificates.
    """

    CLIENT_LOCAL = 'local'
    CLIENT_RUNNER = 'runner'
    CLIENT_WHEEL = 'wheel'

    OUTPUT_RAW = 'raw'
    OUTPUT_JSON = 'json'
    OUTPUT_DICT = 'dict'

    def __init__(self, url, username=None, passwd=None, eauth='pam', trust_host=False):
        self.url = url
        self.username = username
        self.password = passwd
        self.eauth = eauth
        self.trust_host = trust_host
        self.token = None
        self.token_expire = 0
        self.timeout = 60
        self.max_retries = 3
        self.lookup_interval = 1
        self.session = self._new_session()

        self.log = logging.getLogger(__name__)

    def _new_session(self):
        """
        Creates a new requests Session

        Returns:
            request.Session
        """
        session = requests.Session()
        session.verify = not self.trust_host
        retries = Retry(total=self.max_retries, backoff_factor=5)
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
        except Exception as exc:
            self.log.error(exc)
            raise

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

        retry = 0
        remote_disconnect_exc = None
        while True:
            try:
                ret = self.session.post(
                    url=urljoin(self.url, path),
                    json=data,
                    headers=headers,
                    timeout=timeout or self.timeout
                )
                return ret
            except requests.exceptions.ConnectionError as exc:
                if 'RemoteDisconnected' in str(exc):
                    remote_disconnect_exc = exc
                    self.log.debug('Connection lost: %s', exc)
                    if retry <= self.max_retries:
                        retry += 1
                        self.log.debug('Sleeping for %s seconds and retrying (%s/%s)',
                                       self.timeout,
                                       retry,
                                       self.max_retries)
                        time.sleep(self.timeout)
                        continue
                raise SaltConnectionError('Unable to access `{}`.'.format(self.url), exc, remote_disconnect_exc)
            except requests.exceptions.ReadTimeout as exc:
                raise SaltConnectionError('Unable to read response from server due to connection timeout.', exc)
            except Exception as exc:
                raise

    @property
    def token_is_expired(self):
        """
        Checks if the token expiration date has been reached

        Returns:
            bool
        """
        now = datetime.now().timestamp()

        if self.token_expire:
            self.log.debug('Time until authentication token expires:: %s', self.token_expire - now)

        if not self.token or self.token_expire < now:
            return True

    def login(self, eauth=None):
        """
        Creates an authenticated session with a salt API server

        Args:
            eauth (str): External authentication method.

        Returns:

        """
        eauth = eauth or self.eauth
        self.log.debug('Authenticating to salt-api using `%s` external authentication...', eauth)
        data = {
            'username': self.username,
            'password': self.password,
            'eauth': eauth
        }

        ret = self.post(path='login', data=data)
        if ret.status_code == 401:
            raise SaltAuthenticationError('Unable to authenticate to salt-api using proved credentials.')

        try:
            self.token = ret.json()['return'][0]['token']
            self.token_expire = ret.json()['return'][0]['expire']
            self.session.headers.update({'X-Auth-Token': self.token})

            self.log.debug('Authentication succeed.')
            date_string = datetime.fromtimestamp(self.token_expire).strftime("%Y-%m-%d %H:%M:%S")
            self.log.debug('Session token will expire on `%s`', date_string)

            return ret.content
        except Exception:
            msg = 'Unable to connect to salt-api at `{}`. Return code: {}'.format(ret.url, ret.status_code)

            if ret.status_code == 503:
                msg += '. Ensure that the salt-master services is running.'
            raise SaltAuthenticationError(msg)

    def execute(self, fun, client=None, target=None, tgt_type=None, args=None, kwargs=None, pillar=None,
                run_async=False, async_wait=False, output='dict', returner=None):
        """
        Executes a function using the salt API.

        Args:
            fun (str): Name of the function to be executed
            client (str): Type of client to use (local, runner or wheel).
                If not specified, the `local` client will be used.
            target (str): The minions that should execute this function.
                If the client is not set to `local`, this parameter will be ignored.
            tgt_type (str): Targeting type
            args (list): List of arguments to be passed to the function.
            kwargs (dict): Dictionary of arguments to be passed to the function.
            pillar (dict): Dictionary of pillar values to be passed to the function. Example: pillar={'sleep': 30}
            run_async (bool): Whether or not to execute the function asynchronously.
                If set to `True`, it will return the job ID.
                If the client is set to `wheel`, this parameter will be ignored.
            async_wait (bool): If this parameter is set to `True`, it will use async clients, just like the `run_async`
                parameter would, but instead of returning the job ID, it will use it to keep pulling the job result
                until it is completed.
                It is basically the same as passing `run_async=True` and calling `Salt.lookup_job`
                with `until_complete=True`.
            output (str): The output format of this method (See output constants specified in this class).
            returner (str): Which salt returner to be passed to the function.

        Returns:
            str, dict: Depends on the format passed to the `output` parameter.
        """

        if self.token_is_expired:
            self.login()

        client = client or Salt.CLIENT_LOCAL
        client_type = client

        if run_async or async_wait and (client != Salt.CLIENT_WHEEL):
            client += '_async'

        data = {
            'client': client,
            'fun': fun,
        }

        if target:
            data.update({'tgt': target})
        if tgt_type:
            data.update({'tgt_type': tgt_type})
        if pillar:
            args = args or []
            args.append('pillar={}'.format(json.dumps(pillar)))
        if args:
            data.update({'arg': args})
        if kwargs:
            if client_type == Salt.CLIENT_LOCAL:
                data.update({'kwarg': kwargs})
            else:
                data.update(**kwargs)

        if returner:
            data.update({'ret': returner})

        self.log.debug('Executing salt command: %s', data)
        ret = self.post(data)
        try:
            content_dict = json.loads(ret.content)
        except json.decoder.JSONDecodeError as exc:
            msg = 'Unable to parse API return as JSON: {}. Returned code:{}. Returned content: {}'.format(
                exc, ret.status_code, ret.content)
            raise SaltReturnParseError(msg)

        if async_wait:
            try:
                jid = content_dict['return'][0]['jid']
                return self.lookup_job(jid, until_complete=True, output=output)
            except KeyError as exc:
                self.log.debug(exc)
                self.log.debug('Unable to retrieve JID. Assuming no jobs were executed.')
                if target:
                    self.log.debug('Targeting might have matched no minions.')
                return dict()

        # if run_async:
        #     return json.loads(ret.content)

        # if output == Salt.OUTPUT_DICT:
        #     return json.loads(ret.content)

        if output == Salt.OUTPUT_RAW:
            return ret.content

        if output == Salt.OUTPUT_JSON:
            return ret.json()

        return content_dict

    def wheel(self, *args, **kwargs):
        """
        Used to send wheel commands to the salt master.

        See:
            Salt.execute method.
        """

        return self.execute(client=Salt.CLIENT_WHEEL, *args, **kwargs)

    def runner(self, *args, **kwargs):
        """
        Used to send commands to be executed by the salt master.

        See:
            Salt.execute method.
        """

        return self.execute(client=Salt.CLIENT_RUNNER, *args, **kwargs)

    def runner_async(self, wait=False, *args, **kwargs):
        """
        Used to send commands to be executed by the salt master asynchronously.

        Args:
            wait (bool, optional): Defaults to False. Whether or not to pool for the job until completed.

        See:
            Salt.execute method.
        """

        return self.runner(run_async=True, async_wait=wait, *args, **kwargs)

    def local(self, *args, **kwargs):
        """
        Used to send commands to be executed by salt minions.

        See:
            Salt.execute method.
        """

        return self.execute(client=Salt.CLIENT_LOCAL, *args, **kwargs)

    def local_async(self, wait=False, *args, **kwargs):
        """
        Used to send commands to be executed by salt minions asynchronously.

        Args:
            wait (bool, optional): Defaults to False. Whether or not to pool for the job until completed.

        See:
            Salt.execute method.
        """

        return self.local(run_async=True, async_wait=wait, *args, **kwargs)

    def lookup_job(self, jid, until_complete=False, interval=None, output='dict'):
        """
        Retrieves information about a SaltStack job.

        Args:
            jid (int): The job ID.
            until_complete (bool): Whether or not to keep pulling the job until it is completed.
            interval (int): Time interval (in seconds) to wait in between checks.
                If not specified, defaults will be used.
                You can also set the global lookup interval using `self.lookup_interval`.
            output (str): The output format of this method (See output constants specified in this class).
        Returns:
            dict: a dictionary containing the job results
        """

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
        ver = {
            'master': ret['Master'],
            'minions': {}
        }

        if 'Up to date' in ret.keys():
            ver['minions'].update(ret['Up to date'])

        if 'Minion requires update' in ret.keys():
            ver['minions'].update(ret['Minion requires update'])
        return ver
