# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import random

import tornado.web
import tornado.gen
import tornado.concurrent


class Source(object):
    waiters = set()

    def sample_get_message(self):
        future = tornado.concurrent.Future()
        rand = random.randint(1, 10)
        if rand > 5:
            future.set_result(str(rand))
        else:
            self.waiters.add(future)
        return future

    def push(self, val):
        for future in self.waiters:
            future.set_result(val)
        self.waiters = set()


source = Source()


class LongPollingHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        futrue = source.sample_get_message()
        msg = yield futrue
        self.set_header("Access-Control-Allow-Origin", "*")
        self.write(msg)


class PushHandler(tornado.web.RequestHandler):
    def get(self):
        val = self.get_argument("value")
        source.push(val)