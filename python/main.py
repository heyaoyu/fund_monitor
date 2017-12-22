# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import tornado.ioloop
import tornado.web
import tornado.gen

from events.user_msgs import UserMsgs

user_msgs = UserMsgs()
from handlers.MainHandler import *
from handlers.LongPollingHandler import *

from events.events import fund_003704_monitor_job, fund_003705_monitor_job


def main():
    url_matches = [
        (r'/', MainHandler),
        (r'/long_poll_v3', LongPollingHandlerV3),
        (r'/push', PushHandler),
    ]
    app = tornado.web.Application(url_matches)
    app.listen(8888)
    periodicCb = tornado.ioloop.PeriodicCallback(callback=fund_003704_monitor_job, callback_time=8000)  # 8000 ms
    periodicCb.start()
    periodicCb2 = tornado.ioloop.PeriodicCallback(callback=fund_003705_monitor_job, callback_time=8000)  # 8000 ms
    periodicCb2.start()
    run_job_for('user')
    tornado.ioloop.IOLoop.current().start()


def run_job_for(user):
    tornado.ioloop.IOLoop.add_future(tornado.ioloop.IOLoop.instance(), fund_003704_monitor_job.register(user),
                                     future_callback)
    tornado.ioloop.IOLoop.add_future(tornado.ioloop.IOLoop.instance(), fund_003705_monitor_job.register(user),
                                     future_callback)


def future_callback(future):
    user_msgs.store_msg_for(future.user, future.result())
    tornado.ioloop.IOLoop.add_future(tornado.ioloop.IOLoop.instance(), future.event_source.register(future.user),
                                     future_callback)


if __name__ == '__main__':
    main()