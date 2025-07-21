from django.core.management.base import BaseCommand
from posvendasapp.models import Equipe, Clientes, Vendas, Produtos, Ocorrencia
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone
from django.db import connection


class Command(BaseCommand):
    help = 'Popula o banco com dados fake para vendas, produtos e ocorrências'

    def handle(self, *args, **options):
        fake = Faker('pt_BR')

        NUM_VENDAS = 20
        TIPOS_PRODUTOS = [
            ('Contato-diaria', 'Contato-diaria'),
            ('Contato-Quinzenal', 'Contato-Quinzenal'),
            ('Solar', 'Armação'),
            ('Receituario', 'Armação'),
            ('Multifocal', 'Lente Oftalmica'),
            ('Visão simples', 'Lente oftalmica'),
        ]
        TIPOS_OCORRENCIA = [
            'Troca-compra errada',
            'Troca-Garantia',
            'Atualização',
            'Manutenção'
        ]

        self.stdout.write('Apagando dados antigos...')
        Ocorrencia.objects.all().delete()
        Produtos.objects.all().delete()
        Vendas.objects.all().delete()

        def reset_sequence_safe(table_name):
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT setval(pg_get_serial_sequence('\"{table_name}\"', 'id'), COALESCE((SELECT MAX(id) FROM \"{table_name}\"), 1), true);"
                )
            self.stdout.write(self.style.SUCCESS(f"Sequência resetada para {table_name}"))

        reset_sequence_safe('posvendasapp_vendas')
        reset_sequence_safe('posvendasapp_produtos')
        reset_sequence_safe('posvendasapp_ocorrencia')

        # Buscando todos os clientes e usuários cadastrados
        clientes = list(Clientes.objects.all())
        usuarios = list(Equipe.objects.all())

        if not clientes or not usuarios:
            self.stdout.write(self.style.ERROR('Não há clientes ou equipe cadastrados para criar vendas.'))
            return

        self.stdout.write('Criando vendas...')
        vendas = []
        for _ in range(NUM_VENDAS):
            cliente = random.choice(clientes)
            vendedor = random.choice(usuarios)
            data_venda = timezone.now().date() - timedelta(days=random.randint(1, 30))
            previsao = random.randint(5, 30)
            venda = Vendas.objects.create(
                cliente=cliente,
                Data_venda=data_venda,
                Previsao=previsao,
                vendedor=vendedor
            )
            vendas.append(venda)

        self.stdout.write('Criando produtos...')
        for venda in vendas:
            num_produtos = random.randint(1, 3)
            for _ in range(num_produtos):
                tipo, tipo_desc = random.choice(TIPOS_PRODUTOS)
                valor_original = random.uniform(50, 400)
                desconto = random.uniform(0, valor_original * 0.3)
                valor_venda = valor_original - desconto
                Produtos.objects.create(
                    venda=venda,
                    Produto=fake.word().title(),
                    tipo=tipo,
                    Valor_venda=round(valor_venda, 2),
                    valor_produto_sem_desconto=round(valor_original, 2),
                )

        self.stdout.write('Criando ocorrências...')
        for venda in vendas:
            if random.random() < 0.5:
                num_ocorrencias = random.randint(1, 2)
                for _ in range(num_ocorrencias):
                    titulo = fake.sentence(nb_words=4)
                    tipo_ocorrencia = random.choice(TIPOS_OCORRENCIA)
                    desc = fake.paragraph(nb_sentences=3)
                    Ocorrencia.objects.create(
                        venda=venda,
                        vendedor=venda.vendedor,
                        titulo_ocorrencia=titulo,
                        tipo_ocorrencia=tipo_ocorrencia,
                        ocorrencia=desc
                    )

        self.stdout.write(self.style.SUCCESS('Vendas, produtos e ocorrências criados com sucesso!'))
