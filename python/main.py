# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

# log
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
# user_msg
from user_msgs import UserMessageManager

user_msg_manager = UserMessageManager()
# handlers
from handlers import *

from jobs import FundMonitorJob, UserMessageFilter


def init_users_msg_job():
    user_msg_store_path = os.path.join(os.path.dirname(__file__), 'user_msg.store')
    if os.path.exists(user_msg_store_path):
        user_msg_manager.load(user_msg_store_path)
    tornado.ioloop.PeriodicCallback(callback=lambda: user_msg_manager.dump(user_msg_store_path),
                                    callback_time=5000).start()  # 5s


fund_jobs = {}


def update_users_jobs():
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'userjob_sample.db')
        job_file = open(db_path, 'r')
        for line in job_file.readlines():
            user, fund_code, min, max = line.split('_')
            if fund_code in fund_jobs.keys():
                user_msg_filters_dict = fund_jobs.get(fund_code, {})
                if user in user_msg_filters_dict.keys():
                    user_msg_filters_dict.get(user).update(min, max)
                else:
                    user_msg_filters_dict[user] = UserMessageFilter(user, min, max)
            else:
                fund_jobs[fund_code] = {user: UserMessageFilter(user, min, max)}
        job_file.close()
        for fund_code, user_msg_filters_dict in fund_jobs.items():
            job = FundMonitorJob(fund_code)
            job.attach_user_msg_filters(user_msg_filters_dict.values())
            job()
    except Exception, e:
        logger.error(e)
    finally:
        current_ioloop = tornado.ioloop.IOLoop.current()
        current_ioloop.add_timeout(current_ioloop.time() + 60, update_users_jobs)


settings = {
    "cookie_secret": "f1rStbArrEL0Fg01d",
}


def main():
    try:
        url_matches = [
            (r'/login', LoginHandler),  # login
            (r'/pop_msgs', LongPollingHandlerV3),  # product
            (r'/get_msgs', WatchAndKeepMsgHandler),  # debug
            (r'/push_msg', PushHandler),  # admin push
        ]
        app = tornado.web.Application(url_matches, **settings)
        app.listen(8888)
        init_users_msg_job()
        update_users_jobs()
        tornado.ioloop.IOLoop.current().start()
    except Exception, e:
        logger.error(e)


if __name__ == '__main__':
    main()