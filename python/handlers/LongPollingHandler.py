# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

from datetime import timedelta

import tornado.web
import tornado.gen
import tornado.concurrent

from main import user_msgs

from events.events import fund_003704_monitor_job, fund_003705_monitor_job, admin_source, AnyFuture


class LongPollingHandlerV3(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        user = 'user'
        msgs = user_msgs.get_msgs_for(user)
        if msgs:
            self.write(str(msgs))
            self.finish()
            return
        try:
            future1 = fund_003704_monitor_job.register(user)
            future2 = fund_003705_monitor_job.register(user)
            future3 = admin_source.register(user, False)
            future = AnyFuture(future1, future2, future3)
            msg = yield tornado.gen.with_timeout(timedelta(seconds=10), future)
            self.write(str(msg))
        except tornado.gen.TimeoutError:
            print "TimeoutErrorExpected_" + str(len(fund_003704_monitor_job.waiters))
            self.write("TimeoutError")
        self.finish()


class PushHandler(tornado.web.RequestHandler):
    def get(self):
        val = self.get_argument("value")
        admin_source.send_msg(val)