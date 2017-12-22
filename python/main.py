# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import tornado.ioloop
import tornado.web

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
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()