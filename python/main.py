# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import os
import time
import logging.config

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

from handlers.LongPollingHandler import *

from events.jobs import FundMonitorJob, UserMessageFilter


def init_users_msg_job():
    user_msg_store_path = os.path.join(os.path.dirname(__file__), 'user_msg.store')
    if os.path.exists(user_msg_store_path):
        user_msg_manager.load(user_msg_store_path)
    tornado.ioloop.PeriodicCallback(callback=lambda: user_msg_manager.dump(user_msg_store_path),
                                    callback_time=5000).start()  # 5s


def init_users_jobs():
    db_path = os.path.join(os.path.dirname(__file__), 'userjob_sample.db')
    job_file = open(db_path, 'r')
    fund_jobs = {}
    for line in job_file.readlines():
        user, fund_code, min, max = line.split('_')
        if fund_code in fund_jobs.keys():
            fund_jobs[fund_code].append(UserMessageFilter(user, min, max))
        else:
            fund_jobs[fund_code] = [UserMessageFilter(user, min, max)]
    for fund_code, user_msg_filters in fund_jobs.items():
        job = FundMonitorJob(fund_code)
        job.attach_user_msg_filters(user_msg_filters)
        tornado.ioloop.PeriodicCallback(callback=job, callback_time=60000).start()  # 60s
    job_file.close()


def main():
    url_matches = [
        (r'/long_poll_v3', LongPollingHandlerV3),  # product
        (r'/msgs', WatchAndKeepMsgHandler),  # debug
        (r'/push', PushHandler),  # admin push
    ]
    app = tornado.web.Application(url_matches)
    app.listen(8888)
    init_users_msg_job()
    init_users_jobs()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()