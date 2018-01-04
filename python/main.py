# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import os
import logging.config

log_path = os.path.join(os.path.dirname(__file__), 'logging.conf')
logging.config.fileConfig(log_path)
logging.getLogger("tornado.access").disabled = False
logging.getLogger("tornado.application").disabled = False
logging.getLogger("tornado.general").disabled = False

import tornado.ioloop
import tornado.web
import tornado.gen

from events.user_msgs import UserMsgManager

user_msg_manager = UserMsgManager()

from handlers.MainHandler import *
from handlers.LongPollingHandler import *

from events.jobs import FundMonitorJob, UserDataHandler


def load_jobs():
    db_path = os.path.join(os.path.dirname(__file__), 'userjob_sample.db')

    fund_003704_monitor_job = FundMonitorJob("003704")
    fund_003704_monitor_job.attach([UserDataHandler('ludi', 1.05, 1.1), UserDataHandler('heyaoyu', 1.02, 1.05)])
    tornado.ioloop.PeriodicCallback(callback=fund_003704_monitor_job, callback_time=10000).start()  # 10s
    fund_003705_monitor_job = FundMonitorJob("003705")
    fund_003705_monitor_job.attach([UserDataHandler('heyaoyu', 0.8, 1.0)])
    tornado.ioloop.PeriodicCallback(callback=fund_003705_monitor_job, callback_time=10000).start()  # 10s


def main():
    url_matches = [
        (r'/', MainHandler),
        (r'/long_poll_v3', LongPollingHandlerV3),
        (r'/push', PushHandler),
    ]
    app = tornado.web.Application(url_matches)
    app.listen(8888)
    load_jobs()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()