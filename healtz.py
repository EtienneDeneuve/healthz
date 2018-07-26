#!/usr/bin/env python
from __future__ import absolute_import
import os
import string
import sys
import yaml
import pyping
import web
import psutil
import json
import pprint
from pathlib import Path

urls = (
    '/', 'healthz',
    '/config', 'WebConfig'
)

global configfile
configfile = './config.yaml'
configuration = None


class WebConfig():
    def GET(self):
        try:
            file = open(configfile, 'r')
            yamlconfig = yaml.safe_load(file)
            configuration = yaml.safe_dump(
                yamlconfig, default_flow_style=False, canonical=False)
            formatHelper = FormatHelper()
        except:
            e = sys.exc_info()[0]
            print e
            configuration = e

        return formatHelper.prettify(configuration)


class FormatHelper:
    def prettify(self, data):
        return pprint.pformat(data, indent=4, width=80)


class Config:
    def __init__(self):
        self.configuration = None

    def create(self, configfile):
        file = open(configfile, 'r')
        self.configuration = yaml.safe_load(file)
        return self.configuration


class healthz:
    def GET(self):
        try:
            configuration = Config().create(configfile)
            formatHelper = FormatHelper()
            x = 0
            error = 0
            data = {}
            for key, value in configuration.items():
                if key == "exclude":
                    tmpdict1 = {}
                    tmpdict = {}
                    if value == True:
                        error = error + 1
                        tmpdict["value"] = value
                        tmpdict["status"] = "nok"
                        tmpdict1["from_config"] = tmpdict
                        data[key] = tmpdict1
                    else:
                        tmpdict["value"] = value
                        tmpdict["status"] = "ok"
                        tmpdict1["from_config"] = tmpdict
                        data[key] = tmpdict1
                if key == "file_exclude_path":
                    tmpdict = {}
                    try:
                        file_exclude_exist = Path(value)
                        my_abs_path = file_exclude_exist.resolve()
                    except FileNotFoundError:
                        tmpdict["file_path"] = value
                        tmpdict["status"] = "OK"
                        data['exclude']['from_file'] = tmpdict
                    else:
                        tmpdict["file_path"] = value
                        tmpdict["status"] = "NOK"
                        data['exclude']['from_file'] = tmpdict
                        error = error + 1
                if key == "ping":
                    if type(value) is list:
                        tmpdict = {}
                        for v in value:
                            tmpdict1 = {}
                            x = x + 1
                            pypi = pyping.ping(v)
                            if pypi.ret_code != 0:
                                tmpdict1[v] = "NOK"
                                tmpdict[x] = tmpdict1
                                data[key] = tmpdict
                                error = error + 1
                            else:
                                tmpdict1[v] = "OK"
                                tmpdict[x] = tmpdict1
                                data[key] = tmpdict
                    else:
                        tmpdict = {}
                        pypi = pyping.ping(value)
                        if pypi.ret_code != 0:
                            tmpdict1[value] = "NOK"
                            data[key] = tmpdict1
                            error = error + 1
                        else:
                            tmpdict1[value] = "OK"
                            data[key] = tmpdict1
                if key == "services":
                    pids = psutil.pids()
                    tmpdict = {}
                    if type(value) is list:
                        x = 1
                        tmpdict2 = {}
                        for v in value:
                            for p in psutil.process_iter():
                                tmpdict1 = {}
                                pinfo = p.as_dict(
                                    attrs=['pid', 'name', 'status'])
                                if v == pinfo['name']:
                                    tmpdict1['status'] = pinfo['status']
                                    tmpdict[key] = tmpdict1
                                    tmpdict2 = tmpdict
                            if tmpdict:
                                data[key] = tmpdict
                            else:
                                for v in value:
                                    tmpdict['status'] = 'not found'
                                    tmpdict['service'] = v
                                    data[key] = tmpdict
                                    print tmpdict
                                    error = error + 1
                    else:
                        for p in psutil.process_iter():
                            pinfo = p.as_dict(attrs=['pid', 'name', 'status'])
                            if value in pinfo['name']:
                                tmpdict1['status'] = pinfo['status']
                                tmpdict[key][value] = tmpdict1
                        if any(tmpdict) != True:
                            tmpdict['status'] = 'not found'
                            tmpdict['service'] = value
                            data[key] = tmpdict
                            error = error + 1
            if error != 0:
                web.ctx.status = '503 Service Unavailable'
                formatHelper = FormatHelper()
                return "Something is wrong in :<br/>" + formatHelper.prettify(json.dumps(data))
            else:
                return formatHelper.prettify(data)
        except Exception, e:
            exc_tuple = sys.exc_info()
            print "error " + str(e.message)
            return "error " + str(e.message)


def notfound(message):
    return web.notfound(message)


app = web.application(urls, locals())
app.notfound = notfound
if __name__ == "__main__":

    app.run()
