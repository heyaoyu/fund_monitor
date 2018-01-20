from celery import Celery

mysql_celery_app = Celery('mysql_celery', include=['celery_mysql_task'], backend='redis://127.0.0.1:6379',
                      broker='amqp://guest:guest@127.0.0.1:5672//')