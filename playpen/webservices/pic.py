# -*- coding: utf-8 -*-
#
# Copyright © 2011 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

"""
Pulp Interactive Client
This module is meant to be imported to talk to pulp webservices interactively
from an interpreter. It provides convenience methods for connecting to pulp as
well as performing many common pulp tasks.
"""

import base64
import httplib
import json
import os
import sys
import types

_host = 'localhost'
_port = 443
_path_prefix = '/pulp/api'
_user = 'admin'
_password = 'admin'

# connection management -------------------------------------------------------

_connection = None

def connect():
    global _connection
    _connection = httplib.HTTPSConnection(_host, _port)

# requests --------------------------------------------------------------------

class RequestError(Exception):
    pass


def _auth_header():
    raw = ':'.join((_user, _password))
    encoded = base64.encodestring(raw)[:-1]
    return {'Authorization': 'Basic %s' % encoded}


def _request(method, path, body=None):
    if _connection is None:
        raise RuntimeError('You must run connect() before making requests')
    if not isinstance(body, types.NoneType):
        body = json.dumps(body)
    _connection.request(method,
                        _path_prefix + path,
                        body=body,
                        headers=_auth_header())
    response = _connection.getresponse()
    response_body = response.read()
    try:
        response_body = json.loads(response_body)
    except:
        pass
    if response.status > 299:
        raise RequestError('Server response: %d\n%s' %
                           (response.status, response_body))
    return (response.status, response_body)


def _query_params(params):
    for k, v in params.items():
        if isinstance(v, basestring):
            params[k] = [v]
    return '&'.join('%s=%s' % (k, v) for k in params for v in params[k])


def GET(path, **params):
    path = '?'.join((path, _query_params(params)))
    return _request('GET', path)


def PUT(path, body):
    return _request('PUT', path, body)


def POST(path, body=None):
    return _request('POST', path, body)


def DELETE(path):
    return _request('DELETE', path)

# repo management -------------------------------------------------------------

def list_repos():
    return GET('/repositories/')


def get_repo(id):
    return GET('/repositories/%s/' % id)


def create_repo(id, name=None, arch='noarch', **kwargs):
    """
    Acceptable keyword arguments are any arguments for a new Repo model.
    Common ones are: feed and sync_schedule
    """
    kwargs.update({'id': id, 'name': name or id, 'arch': arch})
    return POST('/repositories/', kwargs)


def update_repo(id, **kwargs):
    """
    Acceptable keyword arguments are any arguments for a new Repo model.
    Common ones are: feed and sync_schedule
    """
    return PUT('/repositories/%s/' % id, kwargs)


def delete_repo(id):
    return DELETE('/repositories/%s/' % id)


def schedules():
    """
    List the sync schedules for all the repositories.
    """
    return GET('/repositories/schedules/')


def sync_history(id):
    return GET('/repositories/%s/history/sync/' % id)

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    print >> sys.stderr, 'Not a script, import as a module in an interpreter'
    sys.exit(os.EX_USAGE)
