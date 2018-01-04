# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import logging

logger = logging.getLogger()
import urllib2
import time
import json

from main import user_msg_manager

from datetime import timedelta, datetime


def is_A_market_opening():
    utc_ts = datetime.utcnow()
    bj_ts = utc_ts + timedelta(hours=8)
    if bj_ts.weekday() + 1 in [6, 7]:
        return False
    _9_30 = bj_ts.replace(hour=9, minute=30, second=0, microsecond=0)
    _11_30 = bj_ts.replace(hour=11, minute=30, second=0, microsecond=0)
    _13_00 = bj_ts.replace(hour=13, minute=0, second=0, microsecond=0)
    _15_00 = bj_ts.replace(hour=15, minute=0, second=0, microsecond=0)
    if (_9_30 <= bj_ts and bj_ts <= _11_30) or (_13_00 <= bj_ts and bj_ts <= _15_00):
        return True
    else:
        return False


def can_stock_fund_monitor():
    utc_ts = datetime.utcnow()
    bj_ts = utc_ts + timedelta(hours=8)
    if bj_ts.weekday() + 1 in [6, 7]:
        return False
    _14_30 = bj_ts.replace(hour=14, minute=30, second=0, microsecond=0)
    _15_00 = bj_ts.replace(hour=15, minute=0, second=0, microsecond=0)
    if _14_30 <= bj_ts and bj_ts <= _15_00:
        return True
    else:
        return False


def millsecondsOfNow():
    return (int(round(time.time() * 1000)))


class UserDataHandler(object):
    def __init__(self, user, min, max, interval=500):
        self.user = user
        self.min = min
        self.max = max
        self.interval = interval
        self.last_sent = None

    def shouldTake(self, data):
        # at least 1 msg per day
        utc_ts = datetime.utcnow()
        bj_ts = utc_ts + timedelta(hours=8)
        _15_00 = bj_ts.replace(hour=15, minute=0, second=0, microsecond=0)
        delta = _15_00 - bj_ts
        if delta.total_seconds() > 0 and delta.total_seconds() <= 60:
            return True
        if self.last_sent is None or bj_ts - self.last_sent > self.interval:
            if data <= self.min or data >= self.max:
                self.last_sent = bj_ts
                return True
        return False


class FundMonitorJob(object):
    FUND_URL_TEMPLATE = "http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={ts}"
    PREFIX = "jsonpgz('"
    SUFFIX = "');"

    def __init__(self, fund_code):
        super(FundMonitorJob, self).__init__()
        self.fund_code = fund_code

    def attach(self, user_data_handlers):
        self.user_data_handlers = user_data_handlers

    @staticmethod
    def to_json(s):
        return "{" + s[len(FundMonitorJob.PREFIX):len(s) - len(FundMonitorJob.SUFFIX)] + "}";

    def __call__(self, *args, **kwargs):
        if not is_A_market_opening():
            return
        url = FundMonitorJob.FUND_URL_TEMPLATE.format(fund_code=self.fund_code, ts=millsecondsOfNow())
        response_str = urllib2.urlopen(url).read()
        json_str = FundMonitorJob.to_json(response_str)
        json_object = json.loads(json_str)
        logger.info(u'估值时间:' + json_object['gztime'] + u'_单位净值:' + json_object['dwjz'] + u'_估算值:' + json_object['gsz'])
        users = []
        for user_data_handler in self.user_data_handlers:
            if user_data_handler.shouldTake(float(json_object['gsz'])):
                users.append(user_data_handler.user)
        user_msg_manager.store_users_msg(users, json_str)


class AdminMessageSource(object):
    def __init__(self):
        super(AdminMessageSource, self).__init__()

    def send_msg(self, msg):
        user_msg_manager.store_users_msg('all', msg)


admin_source = AdminMessageSource()