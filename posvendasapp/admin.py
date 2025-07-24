from django.contrib import admin
from .models import Clientes, Vendas, Produtos,Equipe,Ocorrencia
from django.forms.models import BaseInlineFormSet
from django.contrib import admin, messages
from django.contrib.auth.models import User
from axes.models import AccessLog

# Função de ação para liberar bloqueio
def liberar_bloqueio(modeladmin, request, queryset):
    total_deletados = 0
    for user in queryset:
        deletados, _ = AccessLog.objects.filter(username=user.username).delete()
        total_deletados += deletados
    messages.success(request, f'Bloqueio liberado para {queryset.count()} usuário(s). Total de registros deletados: {total_deletados}.')
liberar_bloqueio.short_description = "Liberar bloqueio de usuários selecionados"

# Admin customizado do User com a ação
class UserAdmin(admin.ModelAdmin):
    actions = [liberar_bloqueio]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class OcorrenciaInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj=super().save_new(form, commit=False)
        if not obj.vendedor_id and hasattr(self.request.user,'equipe'):
            obj.vendedor=self.request.user.equipe
            if commit:
                obj.save()
        return obj

# Produtos Inline em Vendas
class ProdutosInline(admin.TabularInline):
    model = Produtos
    extra = 0
    readonly_fields = ('desconto_formatada',)


# Vendas Inline em Clientes
class VendasInline(admin.TabularInline):
    model = Vendas
    extra = 0
    readonly_fields = ('pk','Data_venda','valor_total_venda_formatada', 'previsao_de_retorno','get_vendedor_username')
    fields = ('pk','Data_venda','valor_total_venda_formatada', 'previsao_de_retorno','get_vendedor_username')
    fk_name = 'cliente'# aqui usa o campo

    def  get_vendedor_username(self,obj):
        return obj.vendedor.Usuario.username
    get_vendedor_username.short_description = 'Vendedor'

class OcorrenciaInline(admin.TabularInline):
    model = Ocorrencia
    extra = 0
    fk_name = 'venda'
    formset = OcorrenciaInlineFormSet
    readonly_fields = ('data_correncia','venda','get_vendedor_username',)
    fields = ('data_correncia','get_vendedor_username','tipo_ocorrencia','titulo_ocorrencia',)

    def get_vendedor_username(self, obj):
        if obj.vendedor:
            return obj.vendedor.Usuario.username
        return 'Ainda não definido'
    get_vendedor_username.short_description = 'Vendedor'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset



#admin equipe-vendedores e outros cargos
@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('get_username','Cargo','get_is_active')
    search_fields = ('get_username','Cargo')
    list_filter = ('Usuario__is_active',)
    actions = ['liberar_usuario']

    def get_username(self, obj):
        return obj.Usuario.username
    get_username.short_description = 'Usuário'

    def get_is_active(self,obj):
        return obj.Usuario.is_active
    get_is_active.boolean = True
    get_is_active.short_description = 'Liberado'


    def liberar_usuario(self,request,queryset):
        updated=0
        for equipe in queryset:
            if not equipe.Usuario.is_active:
                equipe.Usuario.is_active=True
                equipe.Usuario.save()
                updated += 1
        self.message_user(request,f'{updated} registro(s) liberado(s).')
    liberar_usuario.short_description = 'Liberar usuarios'




# Admin de Clientes com Vendas Inline
@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('id','Nome', 'contato', 'valor_total_venda_do_cliente_formatada','cpf')
    search_fields = ('Nome', 'contato','cpf')
    inlines = [VendasInline]
    readonly_fields = ('valor_total_venda_do_cliente_formatada',)


# Admin de Vendas com Produtos Inline
@admin.register(Vendas)
class VendasAdmin(admin.ModelAdmin):
    list_display = ('id','cliente', 'Data_venda', 'previsao_de_retorno', 'valor_total_venda_formatada','vendedor')
    search_fields = ('cliente__Nome','vendedor__Usuario__username')
    list_filter = ('Data_venda',)
    inlines = [ProdutosInline,OcorrenciaInline]
    readonly_fields = ('valor_total_venda_formatada', 'previsao_de_retorno','vendedor')

    def  get_vendedor_username(self,obj):
        return obj.vendedor.Usuario.username
    get_vendedor_username.short_description = 'Vendedor'

    def save_model(self, request, obj, form, change):
        if not obj.vendedor_id and hasattr(request.user, 'equipe'):
            obj.vendedor = request.user.equipe
        super().save_model(request, obj, form, change)

@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ('data_correncia','get_vendedor_username','tipo_ocorrencia','titulo_ocorrencia')
    search_fields = ('tipo_ocorrencia','pk','vendedor__Usuario__username')
    list_filter = ('tipo_ocorrencia','vendedor__Usuario__username','titulo_ocorrencia')
    readonly_fields = ('data_correncia','venda','get_vendedor_username')

    def  get_vendedor_username(self,obj):
        return obj.vendedor.Usuario.username
    get_vendedor_username.short_description = 'Vendedor'


# Admin de Produtos isolado (opcional)
@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('id','Produto', 'tipo', 'venda', 'Valor_venda', 'valor_produto_sem_desconto', 'desconto_formatada')
    search_fields = ('Produto', 'tipo','venda__cliente__Nome')#filtro do djangoadmin para Fk
    list_filter = ('tipo', 'venda__cliente__Nome')
