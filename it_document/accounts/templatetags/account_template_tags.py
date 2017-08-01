from django import template
from document.models import ActivityLog

register = template.Library()


@register.inclusion_tag('accounts/activity_log.html')
def get_activity_log(user):
    return {'logs': ActivityLog.objects.filter(user=user).order_by('-time')[:4]}
