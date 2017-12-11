# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello, world.")