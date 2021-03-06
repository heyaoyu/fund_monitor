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
    _09_30 = bj_ts.replace(hour=9, minute=30, second=0, microsecond=0)
    _11_30 = bj_ts.replace(hour=11, minute=30, second=0, microsecond=0)
    _13_00 = bj_ts.replace(hour=13, minute=0, second=0, microsecond=0)
    _15_00 = bj_ts.replace(hour=15, minute=0, second=0, microsecond=0)
    if (_09_30 <= bj_ts and bj_ts <= _11_30) or (_13_00 <= bj_ts and bj_ts <= _15_00):
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


class UserMessageFilter(object):
    def __init__(self, user, min, max, interval=500):
        self.user = user
        self.min = float(min)
        self.max = float(max)
        self.interval = float(interval)
        self.last_sent = None

    def update(self, min, max, interval=500):
        self.min = float(min)
        self.max = float(max)
        self.interval = float(interval)

    def shouldTake(self, data):
        # 4 msgs per-day
        utc_ts = datetime.utcnow()
        bj_ts = utc_ts + timedelta(hours=8)
        _09_30 = bj_ts.replace(hour=9, minute=30, second=0, microsecond=0)
        delta = bj_ts - _09_30
        if delta.total_seconds() > 0 and delta.total_seconds() <= 60:
            return 1
        _11_30 = bj_ts.replace(hour=11, minute=30, second=0, microsecond=0)
        delta = _11_30 - bj_ts
        if delta.total_seconds() > 0 and delta.total_seconds() <= 60:
            return 1
        _13_00 = bj_ts.replace(hour=13, minute=0, second=0, microsecond=0)
        delta = bj_ts - _13_00
        if delta.total_seconds() > 0 and delta.total_seconds() <= 60:
            return 1
        _15_00 = bj_ts.replace(hour=15, minute=0, second=0, microsecond=0)
        delta = _15_00 - bj_ts
        if delta.total_seconds() > 0 and delta.total_seconds() <= 60:
            return 1
        if self.last_sent is None or (bj_ts - self.last_sent).total_seconds() > self.interval:
            if data <= self.min or data >= self.max:
                self.last_sent = bj_ts
                return 2
        return False


class FundMonitorJob(object):
    FUND_URL_TEMPLATE = "http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={ts}"
    PREFIX = "jsonpgz('"
    SUFFIX = "');"

    def __init__(self, fund_code):
        super(FundMonitorJob, self).__init__()
        self.fund_code = fund_code

    def attach_user_msg_filters(self, user_msg_filters):
        self.user_msg_filters = user_msg_filters

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
        logger.info(json_str)
        if not json_object:
            return
        for user_msg_filter in self.user_msg_filters:
            ret = user_msg_filter.shouldTake(float(json_object['gsz']))
            if ret:
                json_object['gsz'] = float(json_object['gsz'])
                json_object['type'] = ret
                json_object['max'] = user_msg_filter.max
                json_object['min'] = user_msg_filter.min
                utc_ts = datetime.utcnow()
                bj_ts = utc_ts + timedelta(hours=8)
                json_object['bjtime'] = bj_ts.strftime("%Y-%m-%d %H:%M:%S")
                user_msg_manager.store_user_message_for(user_msg_filter.user, json.dumps(json_object))


class AdminMessageSource(object):
    def __init__(self):
        super(AdminMessageSource, self).__init__()

    def send_msg(self, msg):
        user_msg_manager.store_all_users_message(msg)


admin_source = AdminMessageSource()