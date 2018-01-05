# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import os
import logging.config
import time

log_path = os.path.join(os.path.dirname(__file__), 'logging.conf')
logging.config.fileConfig(log_path)
logging.Formatter.converter = time.gmtime
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
    file = open(db_path, 'r')
    fund_jobs = {}
    for line in file.readlines():
        user, fund_code, min, max = line.split('_')
        if fund_code in fund_jobs.keys():
            fund_jobs[fund_code].append(UserDataHandler(user, min, max))
        else:
            fund_jobs[fund_code] = [UserDataHandler(user, min, max)]
    for fund_code, userdatahandlers in fund_jobs.items():
        job = FundMonitorJob(fund_code)
        job.attach(userdatahandlers)
        tornado.ioloop.PeriodicCallback(callback=job, callback_time=60000).start()  # 60s


def main():
    url_matches = [
        (r'/', MainHandler),
        (r'/long_poll_v3', LongPollingHandlerV3),
        (r'/msgs', WatchAndKeepMsgHandler),
        (r'/push', PushHandler),
    ]
    app = tornado.web.Application(url_matches)
    app.listen(8888)
    load_jobs()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()