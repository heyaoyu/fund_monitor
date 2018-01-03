# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import logging

logger = logging.getLogger()

from datetime import timedelta

import tornado.web
import tornado.gen
import tornado.concurrent

from main import user_msg_manager
from events.jobs import admin_source


class LongPollingHandlerV3(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        user = self.get_argument("user", "user")
        msgs = user_msg_manager.get_msgs_for(user)
        if msgs:
            self.write(str(msgs))
            self.finish()
            return
        try:
            future = user_msg_manager.get_msgs_future_for(user)
            msg = yield tornado.gen.with_timeout(timedelta(seconds=10), future)
            self.write(str(msg))
        except tornado.gen.TimeoutError:
            logger.error("TimeoutErrorExpected_" + str(len(user_msg_manager.get_msgs_object_for(user).waiters)))
            self.write("TimeoutError")
        self.finish()


class PushHandler(tornado.web.RequestHandler):
    def get(self):
        val = self.get_argument("value")
        admin_source.send_msg(val)