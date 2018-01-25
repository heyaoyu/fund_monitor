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


@mysql_celery_app.task
def login(user):
    db = MySQLdb.connect('127.0.0.1', 'root', '', 'finance_assistant')
    cursor = db.cursor()
    ret = ()
    try:
        cursor.execute("select id from user where name='" + user + "'")
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
def save_history_msg(userid, ts, context, detail):
    db = MySQLdb.connect('127.0.0.1', 'root', '', 'finance_assistant')
    cursor = db.cursor()
    try:
        sql = "INSERT INTO `finance_assistant`.`history_record`(`userid`,`ts`,`context`,`detail`) VALUES ({userid},{ts},{context},{detail});"
        cursor.execute(sql.format(userid=userid, ts=ts, context=context, detail=detail))
        db.commit()
    except Exception, e:
        db.rollback()
        logger.error(e)
    finally:
        cursor.close()
        db.close()


@mysql_celery_app.task
def save_all_users_history_msg(ts, context, detail):
    db = MySQLdb.connect('127.0.0.1', 'root', '', 'finance_assistant')
    cursor = db.cursor()
    try:
        cursor.execute("select id from user")
        userids = cursor.fetchall()
        for userid in userids:
            sql = "INSERT INTO `finance_assistant`.`history_record`(`userid`,`ts`,`context`,`detail`) VALUES ({userid},{ts},{context},{detail});"
            cursor.execute(sql.format(userid=userid, ts=ts, context=context, detail=detail))
        db.commit()
    except Exception, e:
        db.rollback()
        logger.error(e)
    finally:
        cursor.close()
        db.close()