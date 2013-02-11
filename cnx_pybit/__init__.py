# -*- coding: utf-8 -*-
"""\
A standalone API for the PyBit web front-end

Author: Michael Mulich
Copyright (c) 2012 Rice University

Parts of the code are derived from the PyBit implementation at
https://github.com/nicholasdavidson/pybit licensed under GPL 2.1.

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""
import sys
import optparse

# Fix the import path to use the local copy of bottle.
from pybitweb import bottle
sys.modules.setdefault('bottle', bottle)

from bottle import response, Bottle
import pybit
from pybitweb.db import Database
from pybitweb.controller import Controller
from pybitweb import job
import cnx_pybit
from cnx_pybit import api


META="PYBIT_WEB_"


def get_app(settings, db, controller):
    app = Bottle()
    app.config={'settings' : settings, 'db' : db, 'controller' : controller}

    @app.error(404)
    def error404(error):
        return 'HTTP Error 404 - Not Found.'

    @app.error(500)
    def error500(error):
        return 'HTTP Error 500 - Internal Server Error.'

    # Things in here are applied to all requests. We need to set this
    #   header so strict browsers can query it using jquery
    #   http://en.wikipedia.org/wiki/Cross-origin_resource_sharing
    @app.hook('after_request')
    def enable_cors():
        response.headers['Access-Control-Allow-Origin'] = '*'
        allowed_methods = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Methods'] = allowed_methods

    app.mount('/api', api.get_api_app(settings, db, controller))
    # The status routes need mounted because the message handlers use
    #   the build request information to send back to the orginal web
    #   front-end which is populated by the recieving web front-end.
    app.mount('/job', job.get_job_app(settings, db, controller))
    return app


def run():
    parser = optparse.OptionParser()
    # options we can override in the config file.
    groupConfigFile = optparse.OptionGroup(parser, "Config File Defaults",
                                           "All the options which have defaults read from a config file.")
    parser.add_option_group(groupConfigFile)
    parser.add_option_group(groupConfigFile)

    parser.add_option("--config", dest="config", default="web/web.conf",
                      help="Config file to read settings from, defaults to web.conf which will be read from configs/ and /etc/pybit/ in turn.",
                      metavar=META + "CONF_FILE")

    parser.add_option("-v", dest="verbose", action="store_true", default=False,
                      help="Turn on verbose messages.", metavar=META+"VERBOSE")
    (options, args) = parser.parse_args()
    (settings, opened_file) = pybit.load_settings(options.config)
    settings = pybit.merge_options(settings, groupConfigFile, options)

    # singleton instance
    myDb = Database(settings['db'])
    # singleton instance - Needs access to both controller and web settings
    buildController = Controller(settings, myDb)

    app = cnx_pybit.get_app(settings, myDb, buildController)
    bottle.debug(options.verbose)
    bottle.run(app=app,
               server=settings['web']['app'],
               host=settings['web']['interface'],
               port=settings['web']['port'],
               reloader=settings['web']['reloader'],
               )
