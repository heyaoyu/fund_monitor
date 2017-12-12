# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import tornado.ioloop
import tornado.web

from handlers.MainHandler import *
from handlers.LongPollingHandler import *

from jobs.callbacks import cmd_print_test_callback, fund_monitor_check_callback


def main():
    url_matches = [
        (r'/', MainHandler),
        (r'/long_poll', LongPollingHandler),
        (r'/push', PushHandler),
    ]
    app = tornado.web.Application(url_matches)
    app.listen(8888)
    # periodicCb = tornado.ioloop.PeriodicCallback(callback=fund_monitor_check_callback, callback_time=1000)  # 1000 ms
    # periodicCb.start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()