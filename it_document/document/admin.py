from django.contrib import admin
from .models import Document, Comment, Level, UserRateDocument


class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('submit_date', 'edited_date')

admin.site.register(Document, DocumentAdmin)
admin.site.register(Comment)
admin.site.register(Level)
admin.site.register(UserRateDocument)
