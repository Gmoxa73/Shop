from celery import Celery
import os

app = Celery('Store_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Store_api.settings')


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')