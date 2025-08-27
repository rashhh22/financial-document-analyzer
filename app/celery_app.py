from celery import Celery
from .settings import settings
celery_app = Celery("fin_doc_analyzer", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.task_serializer = "json"; celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]; celery_app.conf.task_track_started = True
celery_app.conf.worker_max_tasks_per_child = 100
