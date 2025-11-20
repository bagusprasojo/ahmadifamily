from django.db import models
from django.conf import settings


class Gallery(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='galleries_created',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery_images/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Gambar untuk {self.gallery.title}"
