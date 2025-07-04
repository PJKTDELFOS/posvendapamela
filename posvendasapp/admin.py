from django.contrib import admin
from .models import Clientes, Vendas, Produtos,Equipe

# Produtos Inline em Vendas
class ProdutosInline(admin.TabularInline):
    model = Produtos
    extra = 0
    readonly_fields = ('desconto_formatada',)


# Vendas Inline em Clientes
class VendasInline(admin.TabularInline):
    model = Vendas
    extra = 0
    readonly_fields = ('pk','Data_venda','valor_total_venda_formatada', 'previsao_de_returno','get_vendedor_username')
    fields = ('pk','Data_venda','valor_total_venda_formatada', 'previsao_de_returno','get_vendedor_username')
    # fk_name = 'cliente'# aqui usa o campo

    def  get_vendedor_username(self,obj):
        return obj.vendedor.Usuario.username
    get_vendedor_username.short_description = 'Vendedor'



#admin equipe-vendedores e outros cargos
@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('Usuario__username','Cargo')
    search_fields = ('Usuario__username','Cargo')



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
    list_display = ('cliente', 'Data_venda', 'previsao_de_returno', 'valor_total_venda_formatada','vendedor')
    search_fields = ('cliente__Nome','vendedor__Usuario__username')
    list_filter = ('Data_venda',)
    inlines = [ProdutosInline]
    readonly_fields = ('valor_total_venda_formatada', 'previsao_de_returno','vendedor')

    def  get_vendedor_username(self,obj):
        return obj.vendedor.Usuario.username
    get_vendedor_username.short_description = 'Vendedor'


# Admin de Produtos isolado (opcional)
@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('Produto', 'tipo', 'venda', 'Valor_venda', 'valor_produto_sem_desconto', 'desconto_formatada')
    search_fields = ('Produto', 'tipo','venda__cliente__Nome')#filtro do djangoadmin para Fk
    list_filter = ('tipo', 'venda__cliente__Nome')
