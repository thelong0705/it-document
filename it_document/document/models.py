from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

from category.models import Category


class Level(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=200, unique=True)
    topic = models.ManyToManyField(Category, )
    level = models.ManyToManyField(Level)
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
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_documents')
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.rating = self.userratedocument_set.all().aggregate(Avg('rating'))['rating__avg']
        if self.rating is None:
            self.rating = 0
        super().save()


class Comment(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document)
    content = models.TextField()
    submit_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content


class UserRateDocument(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'document')
