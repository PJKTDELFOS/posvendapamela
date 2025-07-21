from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Reseta as sequências de ID para tabelas com autoincremento'

    def handle(self, *args, **kwargs):
        def reset_sequence_safe(table_name):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"""
                        SELECT setval(
                            pg_get_serial_sequence('"{table_name}"', 'id'),
                            COALESCE(MAX(id), 1),
                            false
                        ) FROM "{table_name}"
                        """
                    )
                    self.stdout.write(self.style.SUCCESS(f"Sequência resetada para {table_name}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Ignorado {table_name}: {e}"))

        tabelas = [
            'posvendasapp_clientes',
            'posvendasapp_vendas',
            'posvendasapp_produtos',
            'posvendasapp_ocorrencia',
            # 'posvendasapp_equipe' ← Não tem campo id, por isso deixamos de fora
        ]

        for tabela in tabelas:
            reset_sequence_safe(tabela)
