from django.db import models
from autoslug import AutoSlugField


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = AutoSlugField(populate_from='name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'
