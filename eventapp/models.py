from django.db import models
from ckeditor.fields import RichTextField
from django.conf import settings


class Event(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()  # ubah dari TextField ke RichTextField
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='events_created',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title
    

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_images/')

    def __str__(self):
        return f"Gambar untuk {self.event.title}"
