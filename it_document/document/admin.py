from django.contrib import admin
from .models import Document, Comment, Level, UserRateDocument, ActivityLog


class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('submit_date', 'edited_date')


class ActivityLogAdmin(admin.ModelAdmin):
    readonly_fields = ('time', )


admin.site.register(Document, DocumentAdmin)
admin.site.register(Comment)
admin.site.register(Level)
admin.site.register(UserRateDocument)
admin.site.register(ActivityLog, ActivityLogAdmin)
