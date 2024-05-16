from celelry import Celery
from datetime import timedelta
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_manager.settings')

celery_app = Celery('event_manager')

celery_app.autodiscover_tasks()

celery_app.conf.broker_url = 'amqp://rabbitmq'
celery_app.conf.result_backend = 'rpc://'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'pickle'
celery_app.conf.accept_content = ['json', 'pickle']
celery_app.conf.result_expires = timedelta(days=3)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 5



