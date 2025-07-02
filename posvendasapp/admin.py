from django.contrib import admin
from .models import Clientes, Vendas, Produtos

# Produtos Inline em Vendas
class ProdutosInline(admin.TabularInline):
    model = Produtos
    extra = 0
    readonly_fields = ('desconto_formatada',)


# Vendas Inline em Clientes
class VendasInline(admin.TabularInline):
    model = Vendas
    extra = 0
    readonly_fields = ('valor_total_venda_formatada', 'previsao_de_returno')


# Admin de Clientes com Vendas Inline
@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('Nome', 'contato', 'valor_total_venda_do_cliente_formatada')
    search_fields = ('Nome', 'contato')
    inlines = [VendasInline]
    readonly_fields = ('valor_total_venda_do_cliente_formatada',)


# Admin de Vendas com Produtos Inline
@admin.register(Vendas)
class VendasAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'Data_venda', 'previsao_de_returno', 'valor_total_venda_formatada')
    search_fields = ('cliente__Nome',)
    list_filter = ('Data_venda',)
    inlines = [ProdutosInline]
    readonly_fields = ('valor_total_venda_formatada', 'previsao_de_returno')


# Admin de Produtos isolado (opcional)
@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('Produto', 'tipo', 'venda', 'Valor_venda', 'valor_produto_sem_desconto', 'desconto_formatada')
    search_fields = ('Produto', 'tipo')
    list_filter = ('tipo', 'venda__cliente__Nome')
