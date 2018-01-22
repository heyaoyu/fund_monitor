# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import logging

logger = logging.getLogger()

from datetime import timedelta

import tornado.web
import tornado.gen
import tornado.concurrent

from main import user_msg_manager
from jobs import admin_source


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class LoginHandler(BaseHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Origin", "null")
        user = self.get_argument("user")
        self.set_secure_cookie("user", user)
        self.write({'status': 'ok', 'user': user})


# ErrorCode: 1 - not login, 2 - TimeoutError

class LongPollingHandlerV3(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Origin", "null")
        if self.current_user is None:
            ret = {'status': 'error', 'datas': 'LoginFirst', 'code': 1}
            self.write(ret)
            self.finish()
            return
        user = self.current_user
        msgs = user_msg_manager.pop_user_messages_object_messages_for(user)
        if msgs:
            ret = {'status': 'ok', 'datas': msgs}
            self.write(ret)
            self.finish()
            return
        future = None
        try:
            future = user_msg_manager.get_user_messages_object_future_for(user)
            msg = yield tornado.gen.with_timeout(timedelta(seconds=10), future)
            ret = {'status': 'ok', 'datas': [msg]}
            self.write(ret)
        except tornado.gen.TimeoutError:
            if future:
                user_msg_manager.get_user_messages_object_for(user).clear(future)
            logger.error(
                "TimeoutErrorExpected_" + str(len(user_msg_manager.get_user_messages_object_for(user).waiters)))
            ret = {'status': 'error', 'datas': 'TimeoutError', 'code': 2}
            self.write(ret)
        self.finish()


class WatchAndKeepMsgHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        user = self.get_argument("user", "user")
        msgs = user_msg_manager.get_user_messages_object_messages_for(user)
        if msgs:
            self.write(str(msgs))
        self.finish()


class PushHandler(tornado.web.RequestHandler):
    def get(self):
        val = self.get_argument("value")
        admin_source.send_msg(val)
        self.finish()


import celery_mysql_task


class CeleryTestHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        response = yield tornado.gen.Task(celery_mysql_task.num_of_records.apply_async, args=["user"])
        self.write({'results': response.result})
        self.finish()