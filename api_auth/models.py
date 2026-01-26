from django.contrib.auth.models import User
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField

from Store_api.validators import validate_image_size


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = ThumbnailerImageField(
        upload_to='avatars/',
        blank=True,
        resize_source=dict(size=(800, 800), sharpen=True),
        validators=[validate_image_size]  # см. Шаг 7
    )