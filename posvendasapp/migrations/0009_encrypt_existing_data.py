# posvendasapp/migrations/0009_encrypt_existing_data.py
from django.db import migrations
from django.conf import settings
from cryptography.fernet import Fernet


def encrypt_existing_data(apps, schema_editor):
    """
    Criptografa dados existentes após os campos terem sido criados
    """
    Clientes = apps.get_model('posvendasapp', 'Clientes')

    # Usar a FERNET_KEY do settings
    fernet_key = getattr(settings, 'FERNET_KEY', None)
    if not fernet_key:
        print("❌ FERNET_KEY não encontrada no settings.py")
        return

    if isinstance(fernet_key, str):
        fernet_key = fernet_key.encode()

    try:
        f = Fernet(fernet_key)
    except Exception as e:
        print(f"❌ Erro ao inicializar Fernet: {e}")
        return

    clientes = Clientes.objects.all()
    total_clientes = clientes.count()

    if total_clientes == 0:
        print("ℹ️ Nenhum cliente encontrado para criptografar.")
        return

    print(f"🔄 Iniciando criptografia de {total_clientes} clientes...")

    for i, cliente in enumerate(clientes, 1):
        try:
            needs_save = False

            # Criptografar email
            if cliente.email and not cliente.email_encrypted:
                cliente.email_encrypted = f.encrypt(cliente.email.encode())
                needs_save = True

            # Criptografar CPF
            if cliente.cpf and not cliente.cpf_encrypted:
                cliente.cpf_encrypted = f.encrypt(cliente.cpf.encode())
                needs_save = True

            # Criptografar telefone
            if cliente.tel_contato and not cliente.tel_contato_encrypted:
                cliente.tel_contato_encrypted = f.encrypt(cliente.tel_contato.encode())
                needs_save = True

            # Criptografar aniversário
            if cliente.aniversario and not cliente.aniversario_encrypted:
                aniversario_str = cliente.aniversario.strftime('%Y-%m-%d')
                cliente.aniversario_encrypted = f.encrypt(aniversario_str.encode())
                needs_save = True

            if needs_save:
                cliente.save()

            if i % 50 == 0 or i == total_clientes:
                print(f"📊 Progresso: {i}/{total_clientes} clientes processados ({(i / total_clientes) * 100:.1f}%)")

        except Exception as e:
            print(f"⚠️ Erro ao processar cliente ID {getattr(cliente, 'id', 'N/A')}: {str(e)}")
            continue

    print("✅ Criptografia de dados existentes concluída com sucesso!")


def reverse_encryption(apps, schema_editor):
    """Limpa campos criptografados"""
    Clientes = apps.get_model('posvendasapp', 'Clientes')
    Clientes.objects.all().update(
        email_encrypted=None,
        cpf_encrypted=None,
        tel_contato_encrypted=None,
        aniversario_encrypted=None
    )


class Migration(migrations.Migration):
    dependencies = [
        ('posvendasapp', '0008_add_encrypted_fields'),
    ]

    operations = [
        migrations.RunPython(
            encrypt_existing_data,
            reverse_encryption,
        ),
    ]