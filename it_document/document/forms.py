from django.forms import ModelForm
from .models import Document
from django import forms
from category.models import Category


class DocumentCreateForm(ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'level', 'author', 'link', 'file', 'image', 'review', 'topic')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Title*'
        self.fields['topic'].label = 'Categories*'
        self.fields['level'].label = 'Level*'
        self.fields['level'].help_text = 'Use ctrl or command to select multiple fields'
        self.fields['topic'].help_text = 'Use ctrl or command to select multiple fields'
        self.fields['review'].label = 'Review*'
        self.fields['topic'].widget.attrs = {'id': 'category-choice'}
        self.fields['file'].label = 'File (pdf only)'
