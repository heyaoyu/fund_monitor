# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import random
from datetime import timedelta

import tornado.web
import tornado.gen
import tornado.concurrent


class Source(object):
    waiters = set()

    def sample_get_message(self):
        future = tornado.concurrent.Future()
        # rand = random.randint(1, 10)
        # if rand > 5:
        # future.set_result(str(rand))
        # else:
        # self.waiters.add(future)
        self.waiters.add(future)
        return future

    def push(self, val):
        for future in self.waiters:
            future.set_result(val)
        self.waiters = set()

    def clear_timeout_future(self, future):
        if future in self.waiters:
            self.waiters.remove(future)


source = Source()


class LongPollingHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        try:
            futrue = source.sample_get_message()
            msg = yield tornado.gen.with_timeout(timedelta(seconds=5), futrue)
            self.write(msg)
        except tornado.gen.TimeoutError, e:
            print "TimeoutErrorExpected_" + str(len(source.waiters))
            source.clear_timeout_future(futrue)
            self.write("TimeoutError")


from jobs.callbacks import fund_monitor_check_callback


class LongPollingHandlerV2(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        try:
            futrue = fund_monitor_check_callback.observer.register()
            msg = yield tornado.gen.with_timeout(timedelta(seconds=5), futrue)
            self.write(msg)
        except tornado.gen.TimeoutError:
            print "TimeoutErrorExpected_" + str(len(fund_monitor_check_callback.observer.waiters))
            fund_monitor_check_callback.observer.clear_timeout_future(futrue)
            self.write("TimeoutError")


from events.events import fund_003704_monitor_job, admin_source, AnyFuture


class LongPollingHandlerV3(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        try:
            future1 = fund_003704_monitor_job.register()
            future2 = admin_source.register()
            future = AnyFuture(future1, future2)
            msg = yield tornado.gen.with_timeout(timedelta(seconds=20), future)
            self.write(str(msg))
        except tornado.gen.TimeoutError:
            print "TimeoutErrorExpected_" + str(len(fund_003704_monitor_job.waiters))
            self.write("TimeoutError")


class PushHandler(tornado.web.RequestHandler):
    def get(self):
        val = self.get_argument("value")
        source.push(val)
        admin_source.send_msg(val)