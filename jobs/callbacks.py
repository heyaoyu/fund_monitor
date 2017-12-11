# -*- coding:utf-8 -*-
__author__ = 'heyaoyu'

import urllib2
import time
import json


def millsecondsOfNow():
    return (int(round(time.time() * 1000)))


def cmd_print_test_callback():
    print 1


class FundMonitorJob(object):
    FUND_URL_TEMPLATE = "http://fundgz.1234567.com.cn/js/{fund_code}.js?rt={ts}"
    PREFIX = "jsonpgz('"
    SUFFIX = "');"

    def __init__(self, fund_code, upper_limit, lower_limit):
        self.fund_code = fund_code
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

    @staticmethod
    def to_json(s):
        return "{" + s[len(FundMonitorJob.PREFIX):len(s) - len(FundMonitorJob.SUFFIX)] + "}";

    def __call__(self, *args, **kwargs):
        url = FundMonitorJob.FUND_URL_TEMPLATE.format(fund_code=self.fund_code, ts=millsecondsOfNow())
        response_str = urllib2.urlopen(url).read()
        json_str = FundMonitorJob.to_json(response_str)
        json_object = json.loads(json_str)
        print u'估值时间:' + json_object['gztime'] + u'_单位净值:' + json_object['dwjz'] + u'_估算值:' + json_object['gsz']


fund_monitor_check_callback = FundMonitorJob("003704", "1.05", "1.002")