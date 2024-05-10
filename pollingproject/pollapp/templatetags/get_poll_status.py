from django import template
from pollapp.models import Poll
from django.utils import timezone

register = template.Library()

@register.filter
def get_poll_status(poll_id):
    poll = Poll.objects.filter(id=poll_id).first()
    return "ongoing" if poll.due_date > timezone.now() else "closed"