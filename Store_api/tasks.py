from celery import shared_task
from easy_thumbnails import files
from django.apps import apps


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def create_thumbnails(self, image_field_name, instance_pk, model_path):
    """
    Асинхронное создание миниатюр для изображения
    """
    try:
        model = apps.get_model(model_path)
        instance = model.objects.get(pk=instance_pk)
        image_field = getattr(instance, image_field_name)

        if image_field:
            thumbnailer = files.get_thumbnailer(image_field)
            for alias in THUMBNAIL_ALIASES[''].keys():
                thumbnailer.get_thumbnail(THUMBNAIL_ALIASES[''][alias])

    except Exception as e:
        raise self.retry(exc=e)