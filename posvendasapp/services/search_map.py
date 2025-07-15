from posvendasapp.models import *



mapa_modelos = {
    'cliente': {
        'queryset': Clientes.objects.all(),
        'campos': ['Nome', 'contato']
        # 'Arquivos' removido porque FileField não é pesquisável por texto
    },
    'produto': {
        'queryset': Produtos.objects.select_related('venda').all(),
        'campos': ['Produto', 'tipo']
    },
    'equipe': {
        'queryset': Equipe.objects.select_related('Usuario').all(),
        'campos': ['Usuario__username', 'Cargo']
    },
    'venda': {
        'queryset': Vendas.objects.select_related('cliente', 'vendedor').all(),
        'campos': ['cliente__Nome', 'vendedor__Usuario__username']
        # Removido produto__nome pois produto não é FK direta aqui
    },
    'ocorrencia': {
        'queryset': Ocorrencia.objects.select_related('venda', 'vendedor').all(),
        'campos': ['titulo_ocorrencia', 'tipo_ocorrencia', 'ocorrencia', 'venda__cliente__Nome', 'vendedor__Usuario__username']
    }
}
