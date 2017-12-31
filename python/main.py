# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import tornado.ioloop
import tornado.web
import tornado.gen

from events.user_msgs import UserMsgManager

user_msg_manager = UserMsgManager()

from handlers.MainHandler import *
from handlers.LongPollingHandler import *

from events.jobs import fund_003704_monitor_job, fund_003705_monitor_job


def main():
    url_matches = [
        (r'/', MainHandler),
        (r'/long_poll_v3', LongPollingHandlerV3),
        (r'/push', PushHandler),
    ]
    app = tornado.web.Application(url_matches)
    app.listen(8888)
    fund_003704_monitor_job.attach(['user'])
    periodicCb = tornado.ioloop.PeriodicCallback(callback=fund_003704_monitor_job, callback_time=8000)  # 8000 ms
    periodicCb.start()
    fund_003705_monitor_job.attach(['user'])
    periodicCb2 = tornado.ioloop.PeriodicCallback(callback=fund_003705_monitor_job, callback_time=8000)  # 8000 ms
    periodicCb2.start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()