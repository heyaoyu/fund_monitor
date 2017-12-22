# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

# in-memory user related msgs container
class UserMsgs(object):
    def __init__(self):
        self.msgs = {}

    def get_msgs_for(self, user):
        msgs = self.msgs.get(user, [])
        self.msgs[user] = []
        return msgs

    def store_msg_for(self, user, msg):
        msgs = self.msgs.get(user, [])
        msgs.append(msg)
        self.msgs[user] = msgs
