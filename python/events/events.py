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

    def register(self, user, important=True):
        future = EventSourceFuture(self, user, important)
        self.waiters.add(future)
        return future

    def fire(self, event):
        for future in self.waiters:
            future.set_result(event)
        self.waiters = set()

    def clear(self, future):
        if future in self.waiters:
            self.waiters.remove(future)


def millsecondsOfNow():
    return (int(round(time.time() * 1000)))


class FundMonitorJob(EventSourceMixin):
    FUND_URL_TEMPLATE = "http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={ts}"
    PREFIX = "jsonpgz('"
    SUFFIX = "');"

    def __init__(self, fund_code):
        super(FundMonitorJob, self).__init__(fund_code)
        self.fund_code = fund_code

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
fund_003705_monitor_job = FundMonitorJob("003705")


class AdminMessageSource(EventSourceMixin):
    def __init__(self):
        super(AdminMessageSource, self).__init__("admin")

    def send_msg(self, msg):
        self.fire(msg)


admin_source = AdminMessageSource()
user_msgs = []


class AnyFuture(tornado.concurrent.Future):
    def __init__(self, *futures):
        super(AnyFuture, self).__init__()
        self.futures = futures
        for future in futures:
            future.add_done_callback(self.done_callback)

    def done_callback(self, future):
        # for f in self.futures:
        # if isinstance(f, EventSourceFuture) and not f.done():
        # f.free()
        if not self.done():
            self.set_result(future.result())
        else:
            if future.important:
                user_msgs.append(future.result())


class EventSourceFuture(tornado.concurrent.Future):
    def __init__(self, event_source, user, important):
        super(EventSourceFuture, self).__init__()
        self.event_source = event_source
        self.user = user
        self.important = important

    def free(self):
        self.event_source.clear(self)