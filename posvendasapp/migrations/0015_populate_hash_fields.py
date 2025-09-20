# posvendasapp/migrations/0016_populate_all_hash_fields.py
from django.db import migrations
import hashlib
from cryptography.fernet import InvalidToken
from django.db import migrations
import hashlib
from cryptography.fernet import Fernet,InvalidToken
from django.conf import settings
fernet = Fernet(settings.FERNET_KEY)

def populate_hashes(apps, schema_editor):
    Clientes = apps.get_model('posvendasapp', 'Clientes')

    try:
        from posvendasapp.models import fernet  # seu fernet de criptografia
    except ImportError:
        fernet = None

    for cliente in Clientes.objects.all():
        try:
            # ------------------ CPF ------------------
            cpf_data = cliente.cpf_encrypted
            if cpf_data:
                if isinstance(cpf_data, memoryview):
                    cpf_data = cpf_data.tobytes()
                cpf_decrypt = fernet.decrypt(cpf_data).decode('utf-8')
                numeros = ''.join(filter(str.isdigit, cpf_decrypt))
                cliente.cpf_hash = hashlib.sha256(numeros.encode('utf-8')).hexdigest()

            # ------------------ EMAIL ------------------
            email_data = cliente.email_encrypted
            if email_data:
                if isinstance(email_data, memoryview):
                    email_data = email_data.tobytes()
                email_decrypt = fernet.decrypt(email_data).decode('utf-8')
                cliente.email_hash = hashlib.sha256(email_decrypt.encode('utf-8')).hexdigest()

            # ------------------ TELEFONE ------------------
            tel_data = cliente.tel_contato_encrypted
            if tel_data:
                if isinstance(tel_data, memoryview):
                    tel_data = tel_data.tobytes()
                tel_decrypt = fernet.decrypt(tel_data).decode('utf-8')
                numeros_tel = ''.join(filter(str.isdigit, tel_decrypt))
                cliente.tel_contato_hash = hashlib.sha256(numeros_tel.encode('utf-8')).hexdigest()

            # ------------------ ANIVERSÁRIO ------------------
            aniversario_data = cliente.aniversario_encrypted
            if aniversario_data:
                if isinstance(aniversario_data, memoryview):
                    aniversario_data = aniversario_data.tobytes()
                aniversario_decrypt = fernet.decrypt(aniversario_data).decode('utf-8')
                # Formata como DD/MM/YYYY antes de gerar hash
                from datetime import datetime
                try:
                    aniversario_dt = datetime.fromisoformat(aniversario_decrypt)
                    aniversario_str = aniversario_dt.strftime('%d/%m/%Y')
                    cliente.aniversario_hash = hashlib.sha256(aniversario_str.encode('utf-8')).hexdigest()
                except Exception as e:
                    print(f"Erro ao processar aniversário de {cliente.pk}: {e}")

            cliente.save(update_fields=['cpf_hash', 'email_hash', 'tel_contato_hash', 'aniversario_hash'])

        except (InvalidToken, ValueError, TypeError, AttributeError) as e:
            print(f"Erro ao gerar hash do cliente {cliente.pk}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('posvendasapp', '0014_remove_clientes_email_search_and_more'),  # ajuste para sua última migration
    ]

    operations = [
        migrations.RunPython(populate_hashes),
    ]
