# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import urllib2
import time
import json

import tornado.concurrent


class EventSourceMixin(object):
    def __init__(self, name):
        self.name = name
        self.waiters = set()

    def register(self):
        future = tornado.concurrent.Future()
        self.waiters.add(future)
        return future

    def fire(self, event):
        for future in self.waiters:
            future.set_result(event)
        self.waiters = set()


def millsecondsOfNow():
    return (int(round(time.time() * 1000)))


class FundMonitorJob(EventSourceMixin):
    FUND_URL_TEMPLATE = "http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={ts}"
    PREFIX = "jsonpgz('"
    SUFFIX = "');"

    def __init__(self, fund_code):
        self.fund_code = fund_code
        super(FundMonitorJob, self).__init__(fund_code)

    @staticmethod
    def to_json(s):
        return "{" + s[len(FundMonitorJob.PREFIX):len(s) - len(FundMonitorJob.SUFFIX)] + "}";

    def __call__(self, *args, **kwargs):
        url = FundMonitorJob.FUND_URL_TEMPLATE.format(fund_code=self.fund_code, ts=millsecondsOfNow())
        response_str = urllib2.urlopen(url).read()
        json_str = FundMonitorJob.to_json(response_str)
        json_object = json.loads(json_str)
        print u'估值时间:' + json_object['gztime'] + u'_单位净值:' + json_object['dwjz'] + u'_估算值:' + json_object['gsz']
        self.fire(json_str)


fund_003704_monitor_job = FundMonitorJob("003704")


class AdminMessageSource(EventSourceMixin):
    def __init__(self):
        super(AdminMessageSource, self).__init__("admin")

    def send_msg(self, msg):
        self.fire(msg)


admin_source = AdminMessageSource()


class AnyFuture(tornado.concurrent.Future):
    def __init__(self, *futures):
        super(AnyFuture, self).__init__()
        self.futures = futures
        for future in futures:
            future.add_done_callback(self.done_callback)

    def done_callback(self, future):
        if not self.done():
            ret = [f.result() if f.done() else None for f in self.futures]
            self.set_result(ret)