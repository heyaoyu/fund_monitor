# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import urllib2
import time
import json

from main import user_msg_manager


def millsecondsOfNow():
    return (int(round(time.time() * 1000)))


class FundMonitorJob(object):
    FUND_URL_TEMPLATE = "http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={ts}"
    PREFIX = "jsonpgz('"
    SUFFIX = "');"

    def __init__(self, fund_code):
        super(FundMonitorJob, self).__init__()
        self.fund_code = fund_code

    def attach(self, users):
        self.users = users

    @staticmethod
    def to_json(s):
        return "{" + s[len(FundMonitorJob.PREFIX):len(s) - len(FundMonitorJob.SUFFIX)] + "}";

    def __call__(self, *args, **kwargs):
        url = FundMonitorJob.FUND_URL_TEMPLATE.format(fund_code=self.fund_code, ts=millsecondsOfNow())
        response_str = urllib2.urlopen(url).read()
        json_str = FundMonitorJob.to_json(response_str)
        json_object = json.loads(json_str)
        print u'估值时间:' + json_object['gztime'] + u'_单位净值:' + json_object['dwjz'] + u'_估算值:' + json_object['gsz']
        user_msg_manager.store_users_msg(self.users, json_str)


fund_003704_monitor_job = FundMonitorJob("003704")
fund_003705_monitor_job = FundMonitorJob("003705")


class AdminMessageSource(object):
    def __init__(self):
        super(AdminMessageSource, self).__init__()

    def send_msg(self, msg):
        user_msg_manager.store_users_msg('all', msg)


admin_source = AdminMessageSource()