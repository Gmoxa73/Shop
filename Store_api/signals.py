from django.db.models.signals import post_save, pre_delete
from .tasks import create_thumbnails

def create_thumbnails_on_save(sender, instance, **kwargs):
    if hasattr(instance, 'avatar') and instance.avatar:
        create_thumbnails.delay(
            image_field_name='avatar',
            instance_pk=instance.pk,
            model_path='myapp.UserProfile'
        )
    elif hasattr(instance, 'image') and instance.image:
        create_thumbnails.delay(
            image_field_name='image',
            instance_pk=instance.pk,
            model_path='myapp.Product'
        )

def delete_thumbnails_on_delete(sender, instance, **kwargs):
    for field_name in ['avatar', 'image']:
        if hasattr(instance, field_name):
            field = getattr(instance, field_name)
            if field:
                field.delete_thumbnails()

post_save.connect(create_thumbnails_on_save, sender=UserProfile)
post_save.connect(create_thumbnails_on_save, sender=Product)
pre_delete.connect(delete_thumbnails_on_delete, sender=UserProfile)
pre_delete.connect(delete_thumbnails_on_delete, sender=Product)