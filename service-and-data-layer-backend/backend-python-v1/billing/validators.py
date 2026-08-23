import os

from django.core.exceptions import ValidationError


def validate_file_size(value):
    limit_mb = 5
    if value.size > limit_mb * 1024 * 1024:
        raise ValidationError(f"File size must be <= {limit_mb} MB")


def validate_file_extension(value):
    valid_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Unsupported file extension.")
