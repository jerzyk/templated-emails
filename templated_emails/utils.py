import os
from django.conf import settings
from tasks import User, send_task, use_celery, send

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


def get_email_directories(dir):
    directory_tree = False
    for name in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, name)):
            if directory_tree == False:
                directory_tree = {}
            directory_tree[name] = get_email_directories(os.path.join(dir, name))
    return directory_tree


def send_templated_email(recipients, template_path, context=None,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    fail_silently=False):
    """
        recipients can be either a list of emails or a list of users,
        if it is users the system will change to the language that the
        user has set as theyr mother toungue
    """
    recipient_pks = [r.pk for r in recipients if isinstance(r, User)]
    recipient_emails = [e for e in recipients if not isinstance(e, User)]
    send_callable = send_task.delay if use_celery else send
    send_callable(recipient_pks, recipient_emails, template_path, context, from_email, fail_silently)
