# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'
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
        print str(len(self.waiters)) + ' for ' + self.name

        for future in self.waiters:
            future.set_result(event)
        self.waiters = set()

    def clear(self, future):
        if future in self.waiters:
            self.waiters.remove(future)


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

    def get_msgs_for(self, user):
        msgs = self.all_user_msgs.get(user, [])
        if msgs:
            ret = msgs.get_msgs()
        else:
            ret = UserMsgs(user)
            self.all_user_msgs[user] = ret
        return ret

    def get_msgs_future_for(self, user):
        msgs = self.all_user_msgs.get(user, [])
        if not msgs:
            msgs = UserMsgs(user)
            self.all_user_msgs[user] = msgs
        future = msgs.register()
        return future

    def store_msg_for(self, user, msg):
        msgs = self.all_user_msgs.get(user, [])
        if msgs:
            msgs.append(msg)
        else:
            msgs = UserMsgs(user)
            msgs.append(msg)
        self.all_user_msgs[user] = msgs


class UserMsgs(UserEventSourceMixin):
    def __init__(self, username):
        super(UserMsgs, self).__init__(username)
        self.username = username
        self.msgs = []

    def append(self, msg):
        self.msgs.append(msg)
        self.fire(msg)

    def get_msgs(self):
        ret = self.msgs
        self.msgs = []
        return ret