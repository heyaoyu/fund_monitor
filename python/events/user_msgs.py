# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import logging

logger = logging.getLogger()
import tornado.concurrent


class UserEventSourceMixin(object):
    def __init__(self, name):
        self.name = name
        self.waiters = set()

    def register(self):
        future = tornado.concurrent.Future()
        self.waiters.add(future)
        return future

    def fire(self, event):
        logger.debug('waiters#' + str(len(self.waiters)) + ' for ' + self.name)

        has_receiver = False
        for future in self.waiters:
            has_receiver = True
            future.set_result(event)
        self.waiters = set()
        return has_receiver

    def clear(self, future):
        if future in self.waiters:
            self.waiters.remove(future)


class UserMsgs(UserEventSourceMixin):
    def __init__(self, username):
        super(UserMsgs, self).__init__(username)
        self.username = username
        self.msgs = []

    def append(self, msg):
        logger.info('record msg for ' + self.username)
        has_receiver = self.fire(msg)
        if not has_receiver:
            self.msgs.append(msg)

    def get_msgs(self):
        ret = self.msgs
        self.msgs = []
        return ret


# in-memory user related msgs container
class UserMsgManager(object):
    def __init__(self):
        self.all_user_msgs = {}

    def store_users_msg(self, users, msg):
        if users == 'all':
            for user in self.all_user_msgs.keys():
                self.store_msg_for(user, msg)
        else:
            for user in users:
                self.store_msg_for(user, msg)

    def get_msgs_object_for(self, user):
        msgs = self.all_user_msgs.get(user, [])
        if not msgs:
            msgs = UserMsgs(user)
            self.all_user_msgs[user] = msgs
        return msgs

    def get_msgs_for(self, user):
        msgs = self.get_msgs_object_for(user)
        return msgs.msgs

    def get_msgs_future_for(self, user):
        msgs = self.get_msgs_object_for(user)
        future = msgs.register()
        return future

    def store_msg_for(self, user, msg):
        msgs = self.all_user_msgs.get(user, [])
        if not msgs:
            msgs = UserMsgs(user)
            self.all_user_msgs[user] = msgs
        msgs.append(msg)