from django.db import migrations
import hashlib
from cryptography.fernet import Fernet,InvalidToken
from django.conf import settings
fernet = Fernet(settings.FERNET_KEY)

def populate_cpf_hash(apps, schema_editor):
    Clientes = apps.get_model("posvendasapp", "Clientes")
    for cliente in Clientes.objects.all():
        encrypted = cliente.cpf_encrypted
        if not encrypted:
            continue
        try:
            # converter caso seja memoryview
            if hasattr(encrypted, "tobytes"):
                encrypted = encrypted.tobytes()
            decrypted = fernet.decrypt(encrypted).decode()
            numeros = ''.join(filter(str.isdigit, decrypted))
            cliente.cpf_hash = hashlib.sha256(numeros.encode()).hexdigest()
            cliente.save(update_fields=["cpf_hash"])
        except InvalidToken:
            # se algum dado corrompido, ignora
            continue

class Migration(migrations.Migration):
    dependencies = [
        ("posvendasapp", "0012_remove_clientes_cpf_search_clientes_cpf_hash"),
    ]

    operations = [
        migrations.RunPython(populate_cpf_hash),
    ]