from django.contrib.auth.models import User
from django.db import models
from category.models import Category
from autoslug import AutoSlugField


class Document(models.Model):
    title = models.CharField(max_length=200, unique=True)
    level = models.CharField(max_length=50)
    topic = models.ManyToManyField(Category)
    author = models.CharField(max_length=50, blank=True, null=True)
    submit_date = models.DateField(auto_now_add=True)
    edited_date = models.DateField(auto_now=True)
    link = models.URLField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    image = models.ImageField(upload_to='document_images', default='/document_images/question_mark.jpg')
    review = models.TextField()
    number_of_likes = models.PositiveIntegerField(default=0)
    number_of_views = models.PositiveIntegerField(default=0)
    posted_user = models.ForeignKey(User)
    approve = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from='title')

    def __str__(self):
        return self.title
