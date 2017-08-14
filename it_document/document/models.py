from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from category.models import Category


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', ]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


class Level(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=200, unique=True)
    topic = models.ManyToManyField(Category, )
    level = models.ManyToManyField(Level)
    submit_date = models.DateField(auto_now_add=True)
    edited_date = models.DateField(default=timezone.now)
    link = models.URLField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to='document_files',
                            validators=[validate_file_extension])
    image = models.ImageField(upload_to='document_images', default='/document_images/question_mark.jpg')
    review = models.TextField()
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

    def update_date(self):
        self.edited_date = timezone.now()


class Comment(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document)
    content = models.TextField()
    is_edited = models.BooleanField(default=False);
    submit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class UserRateDocument(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'document')


class ActivityLog(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document, blank=True, null=True)
    verb = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.verb


class Bookmark(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document)
    bookmarked_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'document')


@receiver(post_save, sender=Bookmark)
def create_bookmark_handler(sender, instance, **kwargs):
    user = instance.user
    document = instance.document
    activity = ActivityLog(user=user, document=document, verb='bookmarked')
    activity.save()


@receiver(post_save, sender=Comment)
def create_comment_handler(sender, instance, created, **kwargs):
    user = instance.user
    document = instance.document
    if created:
        activity = ActivityLog(user=user, document=document, verb='commented at')
        activity.save()
    else:
        activity = ActivityLog(user=user, document=document, verb='edited a comment at')
        activity.save()


@receiver(post_save, sender=Document)
def document_save_handler(sender, instance, created, **kwargs):
    user = instance.posted_user
    document = instance
    if created:
        activity = ActivityLog(user=user, document=document, verb='created')
        activity.save()


@receiver(post_delete, sender=Document)
def document_delete_handler(sender, instance, **kwargs):
    user = instance.posted_user
    title = instance.title
    activity = ActivityLog(user=user, verb='deleted', content=title)
    activity.save()
