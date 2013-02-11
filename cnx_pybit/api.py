# -*- coding: utf-8 -*-
"""\
An API for the PyBit web front-end

Author: Michael Mulich
Copyright (c) 2012 Rice University

Parts of the code are derived from the PyBit implementation at
https://github.com/nicholasdavidson/pybit licensed under GPL 2.1.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
from bottle import (
    Bottle, route, run, template, debug,
    HTTPError, response, error, redirect, request,
    )
import jsonpickle
from pybit.models import Transport, JobHistory
from pybitweb import bottle_basic_auth
from pybitweb.db import Database
from pybitweb.bottle_basic_auth import requires_auth
from pybitweb.controller import Controller


def get_api_app(settings, db, controller) :
    app = Bottle()
    app.config = {'settings': settings, 'db': db, 'controller': controller}

    @app.route('/job/', method='POST')
    @app.route('/job/', method='PUT')
    @requires_auth
    def put_job():
        database = app.config['db']
        # Grab all the sent data. And make sure it's all here.
        try:
            data = request.json
            package = data['package']
            version = data['version']

            arch = data['arch']
            suite = data['suite']
            dist = data['dist']
            pkg_format = data['format']
            uri = data['uri']
            method = data.get('method', '')
            vcs_id = data.get('vcs_id', '')
            slave = data.get('slave', 'false')
        except KeyError as err:
            raise err
            response.status = "400 - Required fields missing."
            return


        param_string = lambda l: ', '.join(["{0!r}".format(x) for x in l])
        print("Calling Controller.process_job(" \
              + param_string([dist, arch, version, package,
                              suite, pkg_format,
                              "Transport(" + param_string([None, method,
                                                           uri, vcs_id]) + \
                              ")",
                              ]) \
              + ")")

        # Pass to controller to queue up
        transport = Transport(None, method, uri, vcs_id)
        controller.process_job(dist, arch, version, package,
                               suite, pkg_format, transport)

    return app
