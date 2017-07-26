from django.contrib import admin
from .models import Document, Comment


class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('submit_date', 'edited_date')


admin.site.register(Document, DocumentAdmin)
admin.site.register(Comment)
