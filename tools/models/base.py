from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Tool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    short_description = models.TextField(max_length=300)
    logo = models.ImageField(upload_to='tool_logos/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Tool"
        verbose_name_plural = "Tools"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Tool.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name