from celery_app import mysql_celery_app

import logging

logger = logging.getLogger()

import MySQLdb


@mysql_celery_app.task
def add(x, y):
    return x + y


@mysql_celery_app.task
def num_of_records(table_name):
    db = MySQLdb.connect('127.0.0.1', 'root', '', 'finance_assistant')
    cursor = db.cursor()
    ret = -1
    try:
        cursor.execute("select count(*) from " + table_name)
        ret = cursor.fetchone()
        # db.commit()
    except Exception, e:
        logger.error(e)
        # db.rollback()
    finally:
        cursor.close()
        db.close()
    return ret


@mysql_celery_app.task
def get_all_user_fund_config():
    db = MySQLdb.connect('127.0.0.1', 'root', '', 'finance_assistant')
    cursor = db.cursor()
    ret = ()
    try:
        cursor.execute("select * from user_fund_config")
        ret = cursor.fetchall()
        # db.commit()
    except Exception, e:
        logger.error(e)
        # db.rollback()
    finally:
        cursor.close()
        db.close()
    return ret