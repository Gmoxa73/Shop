
from django.core.exceptions import ValidationError

def validate_image_size(image):
    file_size = image.file.size
    if file_size > 5 * 1024 * 1024:  # 5 МБ
        raise ValidationError("Размер изображения не должен превышать 5 МБ.")