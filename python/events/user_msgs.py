# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import logging

logger = logging.getLogger()
import json
import os
import tornado.concurrent


class EventSourceMixin(object):
    def __init__(self):
        self.waiters = set()

    def register(self):
        future = tornado.concurrent.Future()
        self.waiters.add(future)
        return future

    def fire(self, data):
        logger.debug('waiters#' + str(len(self.waiters)))

        has_receiver = False
        for future in self.waiters:
            has_receiver = True
            future.set_result(data)
        self.waiters = set()
        return has_receiver

    def clear(self, future):
        if future in self.waiters:
            self.waiters.remove(future)


class UserEventSourceMixin(EventSourceMixin):
    def __init__(self, username):
        super(UserEventSourceMixin, self).__init__()
        self.username = username


class UserMessages(UserEventSourceMixin):
    def __init__(self, username, messages=[]):
        super(UserMessages, self).__init__(username)
        self.messages = messages

    def append_message(self, msg):
        logger.info('record msg for ' + self.username)
        has_receiver = self.fire(msg)
        if not has_receiver:
            self.messages.append(msg)

    def pop_messages(self):
        ret = self.messages
        self.messages = []
        return ret

    def get_messages(self):
        return self.messages


# in-memory user related msgs container
class UserMessageManager(object):
    def __init__(self):
        # username -> messages
        self.all_user_msessages = {}

    def load(self, store_file_path):
        try:
            store = open(store_file_path, 'r')
            data_dict = json.load(store, encoding="utf-8")
            for username, msgs in data_dict.items():
                self.all_user_msessages[username] = UserMessages(username, msgs)
            store.close()
        except Exception, e:
            logger.error(e)

    def dump(self, store_file_path):
        try:
            tmp_path = store_file_path + '.tmp'
            tmp_file = open(tmp_path, 'w')
            data_dict = {}
            for k, v in self.all_user_msessages.items():
                data_dict[k] = v.msgs
            json.dump(data_dict, tmp_file)
            tmp_file.close()
            if os.path.exists(store_file_path):
                os.remove(store_file_path)
            os.rename(tmp_path, store_file_path)
        except Exception, e:
            logger.error(e)

    def store_users_message(self, users, msg):
        if users == 'all':
            for user in self.all_user_msessages.keys():
                self.store_user_message_for(user, msg)
        else:
            for user in users:
                self.store_user_message_for(user, msg)

    def get_user_messages_object_for(self, user):
        user_msgs_obj = self.all_user_msessages.get(user, [])
        if not user_msgs_obj:
            user_msgs_obj = UserMessages(user)
            self.all_user_msessages[user] = user_msgs_obj
        return user_msgs_obj

    def get_user_messages_object_messages_for(self, user):
        user_msgs_obj = self.get_user_messages_object_for(user)
        return user_msgs_obj.get_messages()

    def pop_user_messages_object_messages_for(self, user):
        user_msgs_obj = self.get_user_messages_object_for(user)
        return user_msgs_obj.pop_messages()

    def get_user_messages_object_future_for(self, user):
        user_msgs_obj = self.get_user_messages_object_for(user)
        future = user_msgs_obj.register()
        return future

    def store_user_message_for(self, user, msg):
        user_msgs_obj = self.get_user_messages_object_for(user)
        self.all_user_msessages[user] = user_msgs_obj
        user_msgs_obj.append_message(msg)