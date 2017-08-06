from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='user_images', default='/user_images/question_mark.jpg')
    biography = models.TextField(default='')
    number_of_documents = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        if self.user.is_superuser:
            return reverse('admin_page', kwargs={'pk': self.pk})
        return reverse('user_detail', kwargs={'pk': self.pk})
