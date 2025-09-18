from cryptography.fernet import Fernet
from django.conf import settings
import base64


fernet=Fernet(settings.FERNET_KEY)




