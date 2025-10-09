from django.views.generic import DetailView
from posvendasapp.services.Services import Main_services
from django.contrib.auth import  logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic.list import View,ListView
from django.shortcuts import redirect,render
from django.views.generic.edit import DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from.vendasforms import *
from posvendasapp.services.search_map import mapa_modelos
from datetime import date,timedelta
from utils.tools_utils import *
from django.core.paginator import Paginator
from django.db.models import F, FloatField, ExpressionWrapper,Prefetch,DateField,Func,Case,When,Value,IntegerField
from cryptography.fernet import Fernet
import hashlib
fernet_key = getattr(settings, 'FERNET_KEY', None)
if fernet_key:
    if isinstance(fernet_key, str):
        fernet_key = fernet_key.encode()
    fernet = Fernet(fernet_key)
else:
    fernet = None




# Create your views here.
#views de suporte_______________________________________________________________________________________________________
class Login(LoginView):
    template_name = 'posvendasapp/tela_login.html'
    success_url = reverse_lazy('posvendasapp:menuinicial')
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        messages.success(self.request,f'Usuario {form.get_user().username} Logado com Sucesso')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request,f'Credenciais invalidas ou usuario nao ativo')
        return super().form_invalid(form)
class Logout(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        logout(self.request)
        return redirect('posvendasapp:login_sistema')
@login_required
def testelogin(request):
    return render(request, 'posvendasapp/tela_inicial_vazia.html')
class Busca(LoginRequiredMixin,View):

    def get(self, request):
        termo=request.GET.get('q','').strip()
        resultados={}
        if termo:
            for modelo_nome,info in mapa_modelos.items():
                queryset=info['queryset']
                campos=info['campos']
                qs_resultados=Main_services.busca_centralizada(queryset,termo,campos)

                if qs_resultados.exists():
                    resultados[modelo_nome]=qs_resultados


        return render(request, f'posvendasapp/busca_dinamica.html', {
            'termo': termo,
            'resultados': resultados,
        })
@login_required
def busca_cpf(request):
    cpf_buscado = request.GET.get('q', '').strip()
    cpf_numeros = ''.join(filter(str.isdigit, cpf_buscado))
    print("cpf buscado:", cpf_numeros)

    cpf_hash = hashlib.sha256(cpf_numeros.encode()).hexdigest()
    cliente = Clientes.objects.filter(cpf_hash=cpf_hash).first()

    if cliente:
        print("Cliente encontrado:", cliente)
        return redirect('posvendasapp:atualizar_cliente', pk=cliente.pk)
    else:
        print("Cliente não localizado")
        url = reverse('posvendasapp:cadastrar_cliente')
        return redirect(f"{url}?cpf={cpf_buscado}")
@login_required
def pagina_busca_cpf(request):
    return render(request,'posvendasapp/busca_cpf_cliente.html')



#views de equipe________________________________________________________________________________________________________
class CadastrarEquipe(View):
    template_name = 'posvendasapp/cadastro_att_equipe.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,{
            'form_usuario':UsuarioForm(),
            'form_equipe':EquipeForm(),
            'modo': 'criação'
        })

    def post(self, request, *args, **kwargs):
        form_usuario = UsuarioForm(request.POST,Usuario=None)
        form_equipe = EquipeForm(request.POST)
        try:
            Main_services.criar_equipe(request.POST,request.POST,request_user=request.user)
            return redirect('posvendasapp:tabela_equipe')
        except ValidationError as e:
            errors=e.message_dict
            form_usuario.is_valid()
            form_equipe.is_valid()
            return render(request, self.template_name, {
                'form_usuario': form_usuario,
                'form_equipe': form_equipe,
                'modo':'criação',
                'errors':errors,})
class Atualizar_membro_Equipe(LoginRequiredMixin,View):
    template_name = 'posvendasapp/cadastro_att_equipe.html'
    def get(self, request, pk):
        equipe=get_object_or_404(Equipe,pk=pk)
        if user_group_level(request.user)<=user_group_level(equipe.Usuario):
            messages.error(self.request,'Permissão nao autorizada')
            return redirect('posvendasapp:tabela_equipe')
        usuario=equipe.Usuario
        form_usuario=UsuarioForm(instance=usuario,Usuario=usuario)
        form_equipe=EquipeForm(instance=equipe)
            #aqui passa o contexto para os 2 formularios
        return render(request, self.template_name,{
            'form_usuario':form_usuario,
            'form_equipe':form_equipe,
            'modo': 'edição'})

    def post(self, request, pk):
        equipe = get_object_or_404(Equipe, pk=pk)
        usuario = equipe.Usuario
        form_usuario = UsuarioForm(request.POST, instance=usuario, Usuario=usuario)
        form_equipe = EquipeForm(request.POST, instance=equipe)

        if user_group_level(request.user) <= user_group_level(equipe.Usuario):
            messages.error(request, 'Permissão não autorizada')
            return redirect('posvendasapp:tabela_equipe')

        try:
            Main_services.atualizar_equipe(form_usuario, form_equipe,request_user=request.user)
            messages.success(self.request, 'Usuario atualizado com sucesso.')

            return redirect('posvendasapp:tabela_equipe')
        except ValidationError as e :

            form_usuario.is_valid()
            form_equipe.is_valid()
            return render(request, self.template_name, {
                'form_usuario': form_usuario,
                'form_equipe':  form_equipe,
                'modo':'edição',
                'errors': e.message_dict if hasattr(e, 'message_dict') else e.messages
                })
class DeleteEquipe(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        membro = get_object_or_404(Equipe, pk=kwargs['pk'])
        if user_group_level(request.user)<=user_group_level(membro.Usuario):
            messages.error(self.request,'Permissão nao autorizada')
            return redirect('posvendasapp:tabela_equipe')


        try:
            membro.delete()
            messages.warning(request, 'Menbro da Equipe excluído com sucesso!')
        except:
            messages.error(request, 'Erro ao excluir.')

        return redirect('posvendasapp:tabela_equipe')
class Listar_Staff(LoginRequiredMixin,ListView):
    model = Equipe
    template_name = 'posvendasapp/tabela_equipe.html'
    context_object_name = 'equipe'
    paginate_by = 10

    def get_queryset(self):
        queryset = Equipe.objects.order_by('Usuario')
        self.cargo = self.request.GET.get('Cargo', None)
        if self.cargo:
            queryset = queryset.filter(Cargo=self.cargo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cargos'] = Equipe.objects.values_list('Cargo', flat=True).distinct()
        context['filtro_cargo'] = self.cargo  # passa o filtro para o template
        return context
class Membro_Equipe(LoginRequiredMixin,DetailView):
    model = Equipe
    template_name = 'posvendasapp/equipe_ficha.html'
    context_object_name = 'staff'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)

        return context



#views de cliente_______________________________________________________________________________________________________
class Cadastrar_Cliente(LoginRequiredMixin,View):
    template_name = 'posvendasapp/cadastro_att_cliente.html'

    def get(self, request, *args, **kwargs):
        cpf=request.GET.get('cpf','')
        cliente_form=Clienteforms(initial={'cpf':cpf})

        return render(request, self.template_name,{
            'cliente_form':cliente_form,
            'modo':'criação'
        })

    def post(self, request, *args, **kwargs):
        form_cliente=Clienteforms(request.POST,request.FILES)
        try:
            Main_services.cadastrar_cliente(form_cliente)
            return redirect('posvendasapp:menuinicial')#trocar depois para tabela cliente, mudança apenas para teste
        except ValidationError :
            print(form_cliente.errors)
            return render(request, self.template_name, {
                'cliente_form': form_cliente,
                'modo':'criação'
            })
class Atualizar_Cliente(LoginRequiredMixin,View):
    template_name = 'posvendasapp/cadastro_att_cliente.html'
    def get(self, request, *args, **kwargs):
        cliente=get_object_or_404(Clientes,pk=self.kwargs['pk'])
        form_cliente=Clienteforms(instance=cliente)
        return render(request, self.template_name,{
            'cliente_form':form_cliente,
            'modo':'edição',
            'cliente_pk': cliente.pk

        })
    def post(self, request, *args, **kwargs):
        cliente = get_object_or_404(Clientes, pk=self.kwargs['pk'])
        form_cliente = Clienteforms( request.POST, request.FILES,instance=cliente)
        try:
            Main_services.atualizar_clientes(form_cliente)
            return redirect('posvendasapp:menuinicial')
        except ValidationError :
            print(form_cliente.errors)
            return render(request, self.template_name, {
                'cliente_form': form_cliente,
                'modo':'edição',
                'cliente_pk': cliente.pk,

            })
class DeleteCliente(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        cliente = get_object_or_404(Clientes, pk=kwargs['pk'])
        try:
            cliente.delete()
            messages.warning(request, 'Cliente excluído com sucesso!')
        except:
            messages.error(request, 'Erro ao excluir.')

        return redirect('posvendasapp:tabela_cliente')
class Listar_Clientes(LoginRequiredMixin,ListView):
    model = Clientes
    template_name = 'posvendasapp/tabela_clientes.html'
    context_object_name = 'cliente'
    paginate_by = 10

    # def get_queryset(self):
    #     sort_param = self.request.GET.get('sort', '')
    #     filtro_param=self.request.GET.get('filtro', '')
    #     hoje=date.today()
    #
    #     queryset = Clientes.objects.annotate(
    #         eh_aniversariante=Case(
    #             When(aniversario__day=hoje.day, aniversario__month=hoje.month, then=Value(0)),  # menor = vai pro topo
    #             default=Value(1),
    #             output_field=IntegerField()
    #         )
    #     ).order_by('eh_aniversariante', 'Nome')
    #
    #     if filtro_param == 'aniversariantes_mes':
    #         queryset = queryset.filter(aniversario__month=hoje.month)
    #     queryset = queryset.order_by('eh_aniversariante', 'Nome')
    #
    #     # Aplica ordenação manual posterior com base no total
    #     if sort_param in ['valor_total', 'valor_total_asc']:
    #         queryset = list(queryset)
    #         queryset.sort(
    #             key=lambda cliente: cliente.valor_total_venda_do_cliente,
    #             reverse=(sort_param == 'valor_total')
    #         )
    #     elif sort_param == 'nome':
    #         queryset = queryset.order_by('eh_aniversariante','Nome')
    #     elif sort_param == 'nome_desc':
    #         queryset = queryset.order_by('eh_aniversariante','-Nome')
    #     elif sort_param == 'aniversario':
    #         return Clientes.objects.filter(
    #             aniversario__day=hoje.day,
    #             aniversario__month=hoje.month
    #         ).order_by('Nome')
    #     else:
    #         queryset = queryset.order_by('eh_aniversariante','-id')
    #
    #
    #
    #     return queryset
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     hoje = date.today()
    #     context['aniversariantes'] = Clientes.objects.filter(
    #         aniversario_encrypted__day=hoje.day,
    #         aniversario_encrypted__month=hoje.month
    #     )
    #     context['today'] = date.today()
    #     return context
    #
    # def get(self,request,*args,**kwargs):
    #     hoje=date.today()
    #     aniversariantes=Clientes.objects.filter(aniversario_encrypted__day=hoje.day,
    #                                             aniversario_encrypted__month=hoje.month,
    #                                             )
    #     if aniversariantes.exists():
    #         messages.info(self.request,f"🎉 Hoje temos "
    #                                    f"{aniversariantes.count()} cliente(s) fazendo aniversário!")
    #     return super().get(request,*args,**kwargs)
class Cliente(LoginRequiredMixin,DetailView ):
    model = Clientes
    template_name = 'posvendasapp/cliente_ficha.html'
    context_object_name = 'cliente'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.get_object()

        nome_pasta = f"{cliente.id}-{sanitize_name(cliente.Nome)}"
        caminho_pasta = os.path.join(settings.MEDIA_ROOT, 'Clientes', nome_pasta)
        print(caminho_pasta,'caminho pasta debug')

        arquivos = []
        if os.path.exists(caminho_pasta):
            arquivos = os.listdir(caminho_pasta)

        context['arquivos'] = arquivos
        context['nome_pasta'] = nome_pasta
        context['MEDIA_URL'] = settings.MEDIA_URL


        vendas = cliente.Vendas.all()


        nome = self.request.GET.get('nome')
        retorno = self.request.GET.get('retorno')
        valor = self.request.GET.get('valor')

        if nome == 'az':
            vendas = vendas.order_by('cliente__Nome')
        elif nome == 'za':
            vendas = vendas.order_by('-cliente__Nome')


        # ordenação manual para  valor_total_venda se por ser uma  @property
        if valor == 'asc':
            vendas = sorted(vendas, key=lambda v: v.valor_total_venda)
        elif valor == 'dec':
            vendas = sorted(vendas, key=lambda v: v.valor_total_venda, reverse=True)
        # ordenação manual para previsao de retorno se por ser uma  @property
        if valor == 'asc':
            vendas = sorted(vendas, key=lambda v: v.previsao_de_retorno)
        elif valor == 'dec':
            vendas=sorted(vendas, key=lambda v: v.previsao_de_retorno, reverse=True)

        # Paginação
        paginator = Paginator(vendas, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['vendas'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        return context
def delete_arquivos_cliente(request,pk):
    if request.method == 'POST':
        cliente=get_object_or_404(Clientes, pk=pk)
        cliente_nome=f'{cliente.id}-{sanitize_name(cliente.Nome)}'
        caminho_base=os.path.join(settings.MEDIA_ROOT,'Clientes',cliente_nome)
        print(caminho_base,'caminho base')
        arquivo_excluir=request.POST.get('arquivo')
        if arquivo_excluir :
            caminho_arquivo_excluir=os.path.join(caminho_base, arquivo_excluir)
            if os.path.exists(caminho_arquivo_excluir):
                try:
                    os.remove(caminho_arquivo_excluir)
                    messages.success(request, 'Arquivo excluido com sucesso!')
                    print(caminho_arquivo_excluir)
                except Exception as e:
                    print(f"Erro ao deletar o arquivo: {e}")
            else:
                print("Parâmetros inválidos enviados na requisição.")
    return redirect('posvendasapp:cliente',pk=pk)


#views de vendas_______________________________________________________________________________________________________
class Cadastrar_Vendas(LoginRequiredMixin, View):
    template_name = 'posvendasapp/cadastro_vendas.html'

    def get(self, request, *args, **kwargs):
        cliente = Clientes.objects.get(pk=self.kwargs['cliente_pk'])
        vendedor = request.user.equipe
        venda_fake = Vendas(cliente=cliente, vendedor=vendedor)

        form_venda = Vendaforms(cliente=cliente, vendedor=vendedor)
        form_produto_formset = ProdutoFormSet(instance=venda_fake, prefix='produtos')
        ocorrencia_formset = OcorrenciaFormSet(instance=venda_fake, prefix='ocorrencias')
        ocorrencia_formset.request = request  # request nao passa para  formset de forma direta

        return render(request, self.template_name, {
            'form_venda': form_venda,
            'form_produto_formset': form_produto_formset,
            'ocorrencia_formset': ocorrencia_formset,
            'modo': 'criação'
        })

    def post(self, request, *args, **kwargs):
        cliente = Clientes.objects.get(pk=self.kwargs['cliente_pk'])
        vendedor = request.user.equipe
        venda_fake = Vendas(cliente=cliente, vendedor=vendedor)

        form_venda = Vendaforms(request.POST, cliente=cliente, vendedor=vendedor)
        form_produto_formset = ProdutoFormSet(request.POST, instance=venda_fake, prefix='produtos')
        ocorrencia_formset = OcorrenciaFormSet(request.POST, instance=venda_fake, prefix='ocorrencias')
        ocorrencia_formset.request = request  # ✅ Correto

        try:
            Main_services.cadastrar_venda(
                dados_venda=request.POST,
                dados_produto=request.POST,
                dados_ocorrencia=request.POST,
                cliente=cliente,
                vendedor=vendedor,
                request=request
            )
            return redirect('posvendasapp:tabela_venda')
        except ValidationError as e:
            return render(request, self.template_name, {
                'form_venda': form_venda,
                'form_produto_formset': form_produto_formset,
                'ocorrencia_formset': ocorrencia_formset,
                'errors': e,
                'modo': 'criação'
            })
class Atualizar_Vendas(LoginRequiredMixin, View):
    template_name = 'posvendasapp/cadastro_vendas.html'

    def get(self, request, *args, **kwargs):
        venda = get_object_or_404(Vendas, pk=self.kwargs['pk'])
        cliente = venda.cliente
        vendedor = venda.vendedor

        form_venda = Vendaforms(instance=venda, cliente=cliente, vendedor=vendedor)
        produto_formset = ProdutoFormSet(instance=venda,prefix='produtos')
        ocorrencia_formset = OcorrenciaFormSet(instance=venda,prefix='ocorrencias')
        ocorrencia_formset.request = request  # ✅ necessário

        return render(request, self.template_name, {
            'venda': venda,
            'form_venda': form_venda,
            'form_produto_formset': produto_formset,
            'ocorrencia_formset': ocorrencia_formset,
            'modo': 'edição'
        })

    def post(self, request, *args, **kwargs):
        venda = get_object_or_404(Vendas, pk=self.kwargs['pk'])
        cliente = venda.cliente
        vendedor = venda.vendedor

        try:
            Main_services.atualizar_venda(
                dados_venda=request.POST,
                dados_produto=request.POST,
                dados_ocorrencia=request.POST,
                venda=venda,
                cliente=cliente,
                vendedor=vendedor,
                request=request
            )
            return redirect('posvendasapp:tabela_venda')
        except ValidationError as e:
            form_venda = Vendaforms(request.POST, instance=venda, cliente=cliente, vendedor=vendedor)
            produto_formset = ProdutoFormSet(request.POST, instance=venda, prefix='produtos')
            ocorrencia_formset = OcorrenciaFormSet(request.POST, instance=venda, prefix='ocorrencias')
            ocorrencia_formset.request = request  # aqui também

            return render(request, self.template_name, {
                'venda':venda,
                'form_venda': form_venda,
                'form_produto_formset': produto_formset,
                'ocorrencia_formset': ocorrencia_formset,
                'errors': e,
                'modo': 'edição'
            })
class Listar_Vendas(LoginRequiredMixin, ListView):
    model = Vendas
    template_name = 'posvendasapp/tabela_vendas.html'
    context_object_name = 'vendas'
    paginate_by = 10

    def get_queryset(self):
        produtos_prefetch = Prefetch('produtos_vendidos')  # garantir prefetch
        qs = Vendas.objects.select_related('cliente', 'vendedor') \
            .prefetch_related(produtos_prefetch, 'ocorrencias_venda')

        nome = self.request.GET.get('nome', '')
        valor = self.request.GET.get('valor', '')
        retorno = self.request.GET.get('retorno', '')

        # Ordenação por nome
        if nome == 'az':
            return qs.order_by('cliente__Nome')
        elif nome == 'za':
            return qs.order_by('-cliente__Nome')

        # Ordenação por valor total (manual)
        if valor in ['asc', 'dec']:
            lista = list(qs)  # Força avaliação com prefetch aplicado
            for venda in lista:
                list(venda.produtos_vendidos.all())  # Força carregar os produtos aqui

            lista.sort(
                key=lambda v: v.valor_total_venda if v.valor_total_venda is not None else 0,
                reverse=(valor == 'dec')
            )
            return lista

        # Ordenação por data de retorno (manual)
        if retorno in ['asc', 'dec']:
            lista = list(qs)
            lista.sort(
                key=lambda v: (v.Data_venda + timedelta(days=v.Previsao))
                if v.Data_venda and v.Previsao else date.min,
                reverse=(retorno == 'dec')
            )
            return lista



        qs=qs.annotate(
            previsao_retorno_ordenada_auto_lista=ExpressionWrapper(
                F('Data_venda')+Func(
                    F('Previsao'),
                    function='make_interval',
                    template="%(function)s(days => %(expressions)s)"),
                    output_field=DateField(),
            )
        ).order_by('previsao_retorno_ordenada_auto_lista')



        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        # paginação manual
        if isinstance(qs, list):
            paginator = Paginator(qs, self.paginate_by)
            page_number = self.request.GET.get('page') or 1
            page_obj = paginator.get_page(page_number)
        else:
            paginator = Paginator(qs, self.paginate_by)
            page_number = self.request.GET.get('page') or 1
            page_obj = paginator.get_page(page_number)

        context['vendas'] = page_obj
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['is_paginated'] = page_obj.has_other_pages()

        return context
class Delete_Venda_via_tabela_geral(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        venda_deletada = get_object_or_404(Vendas, pk=kwargs['pk'])

        try:
            venda_deletada.delete()
            messages.warning(request, 'venda excluída com sucesso!')
        except:
            messages.error(request, 'Erro ao excluir: venda está vinculado a outros registros.')

        return redirect('posvendasapp:tabela_venda')

class Delete_Venda_via_tabela_ficha_cliente(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        venda_deletada = get_object_or_404(Vendas, pk=kwargs['pk'])
        cliente=venda_deletada.cliente

        try:
            venda_deletada.delete()
            messages.warning(request, 'venda excluída com sucesso!')
        except:
            messages.error(request, 'Erro ao excluir: venda está vinculado a outros registros.')

        return redirect('posvendasapp:cliente',pk=cliente.pk)
class Venda_(LoginRequiredMixin,DetailView ):
    model = Vendas
    template_name = 'posvendasapp/venda_ficha.html'
    context_object_name = 'venda'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        venda=self.get_object()
        produtos=venda.produtos_vendidos.all()
        #querrystrings

        # valor_venda = self.request.GET.get('valor_venda')
        # valor_sem_desconto=self.request.GET.get('valor_sem_desconto')
        # desconto=self.request.GET.get('desconto')

        sort=self.request.GET.get('sort','')


        #ordenações

        if sort == 'valor_venda':
            produtos = produtos.order_by('Valor_venda')
        elif sort == 'valor_venda_asc':
            produtos = produtos.order_by('-Valor_venda')

        elif sort == 'valor_produto_sem_desconto':
            produtos = produtos.order_by('valor_produto_sem_desconto')
        elif sort == 'valor_produto_sem_desconto_asc':
            produtos = produtos.order_by('-valor_produto_sem_desconto')


        # ordenação manual para  desconto  por ser uma  @property
        if sort == 'Valor_venda':
            produtos = produtos.order_by('-Valor_venda')
        elif sort == 'Valor_venda_asc':
            produtos = produtos.order_by('Valor_venda')
        elif sort == 'valor_produto_sem_desconto':
            produtos = produtos.order_by('-valor_produto_sem_desconto')
        elif sort == 'valor_produto_sem_desconto_asc':
            produtos = produtos.order_by('valor_produto_sem_desconto')
        elif sort == 'desconto':
            produtos = sorted(produtos, key=lambda p: p.desconto, reverse=True)
        elif sort == 'desconto_asc':
            produtos = sorted(produtos, key=lambda p: p.desconto)

        # Paginação
        paginator = Paginator(produtos, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['produtos'] = page_obj
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        return context
class Deletar_Produto(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        venda_acessada=get_object_or_404(Vendas, pk=kwargs['pk'])
        produto_deletado = get_object_or_404(Produtos, pk=kwargs['produto_pk'],venda=venda_acessada)
        try:
            produto_deletado.delete()
            messages.warning(request, 'Produto excluído com sucesso!')
        except :
            messages.error(request, 'Erro ao excluir: produto está vinculado a outros registros.')

        return redirect('posvendasapp:atualizar_venda',pk=venda_acessada.pk)
class Delete_produto_tabela_geral(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        produto = get_object_or_404(Produtos, pk=kwargs['produto_pk'])

        try:
            produto.delete()
            messages.warning(request, 'Produto excluído com sucesso!')
        except :
            messages.error(request, 'Erro ao excluir: produto está vinculado a outros registros.')

        return redirect('posvendasapp:tabela_produtos_vendidos')
class Delete_produto_tabela_venda_individual(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        produto = get_object_or_404(Produtos, pk=kwargs['produto_pk'])
        venda=produto.venda

        try:
            produto.delete()
            messages.warning(request, 'Produto excluído da venda com sucesso!')
        except :
            messages.error(request, 'Erro ao excluir: produto .')

        return redirect('posvendasapp:ficha_venda',pk=venda.pk)

class DeleteOcorrencia(LoginRequiredMixin,DeleteView):
    def post(self, request, *args, **kwargs):
        venda_acessada = get_object_or_404(Vendas, pk=kwargs['pk'])
        ocorrencia_deletado = get_object_or_404(Ocorrencia, pk=kwargs['ocorrencia_pk'], venda=venda_acessada)
        try:
            ocorrencia_deletado.delete()
            messages.warning(request, ' Ocorrencia excluida com sucesso!')
        except:
            messages.error(request, 'Erro ao excluir: Ocorrencia.')

        return redirect('posvendasapp:atualizar_venda',pk=venda_acessada.pk)

class Listar_Produtos_Vendidos(LoginRequiredMixin, ListView):
    model = Produtos
    template_name = 'posvendasapp/tabela_produtos_vendidos.html'
    context_object_name = 'produtos'
    paginate_by = 10

    def get_queryset(self):
        sort_param = self.request.GET.get('sort', '')
        queryset = Produtos.objects.all()

        # Ordenações diretas no banco
        if sort_param == 'Valor_venda':
            queryset = queryset.order_by('-Valor_venda')
        elif sort_param == 'Valor_venda_asc':
            queryset = queryset.order_by('Valor_venda')
        elif sort_param == 'valor_produto_sem_desconto':
            queryset = queryset.order_by('-valor_produto_sem_desconto')
        elif sort_param == 'valor_produto_sem_desconto_asc':
            queryset = queryset.order_by('valor_produto_sem_desconto')
        elif sort_param == 'desconto':
            queryset = queryset.annotate(
                desconto_calc=ExpressionWrapper(
                    100 * (F('valor_produto_sem_desconto') - F('Valor_venda')) / F('valor_produto_sem_desconto'),
                    output_field=FloatField()
                )
            ).order_by('-desconto_calc')
        elif sort_param == 'desconto_asc':
            queryset = queryset.annotate(
                desconto_calc=ExpressionWrapper(
                    100 * (F('valor_produto_sem_desconto') - F('Valor_venda')) / F('valor_produto_sem_desconto'),
                    output_field=FloatField()
                )
            ).order_by('desconto_calc')
        else:
            queryset = queryset.order_by('-id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context