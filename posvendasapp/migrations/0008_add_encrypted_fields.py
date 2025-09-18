# posvendasapp/migrations/0008_add_encrypted_fields.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('posvendasapp', '0007_logacao'),
    ]

    operations = [
        # Apenas adicionar os campos criptografados
        migrations.AddField(
            model_name='clientes',
            name='email_encrypted',
            field=models.BinaryField(blank=True, null=True, verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='clientes',
            name='cpf_encrypted',
            field=models.BinaryField(blank=True, null=True, verbose_name='CPF'),
        ),
        migrations.AddField(
            model_name='clientes',
            name='tel_contato_encrypted',
            field=models.BinaryField(blank=True, null=True, verbose_name='Telefone'),
        ),
        migrations.AddField(
            model_name='clientes',
            name='aniversario_encrypted',
            field=models.BinaryField(blank=True, null=True, verbose_name='aniversario'),
        ),
    ]