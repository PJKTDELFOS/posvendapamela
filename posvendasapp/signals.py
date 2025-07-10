from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in)
def logout_previous_session(sender,user,request, **kwargs):
    current_session_key=request.session.session_key
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
       data=session.get_decoded()
       if data.get('_auth_user_id') ==str(user.id) and session.session_key!=current_session_key:
           session.delete()

