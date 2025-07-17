from posvendasapp.services.Services import Main_services
from django.contrib.auth import  logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic.list import View,ListView
from django.shortcuts import redirect,render
from django.views.generic.edit import DeleteView
import shutil
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from.vendasforms import *
from posvendasapp.services.search_map import mapa_modelos
from datetime import date,timedelta
from django.core.paginator import Paginator
from django.http import  HttpResponseBadRequest
from django.db.models import Q,Sum, F, Value,Prefetch
from django.db.models.functions import Coalesce

# Create your views here.



# Create your views here.


class Login(LoginView):
    template_name = 'posvendasapp/tela_login.html'
    success_url = reverse_lazy('posvendasapp:menuinicial')
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.success_url

class Logout(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        logout(self.request)
        return redirect('posvendasapp:login_sistema')
@login_required
def testelogin(request):
    return render(request, 'posvendasapp/tela_inicial_vazia.html')


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
            Main_services.criar_equipe(request.POST,request.POST)
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

        try:
            Main_services.atualizar_equipe(form_usuario, form_equipe)
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



class DeleteEquipe(LoginRequiredMixin,DeleteView):
    model = Equipe
    success_url = reverse_lazy('posvendasapp:tabela_equipe')
    pk_url_kwarg = 'pk'
    template_name = 'posvendasapp/confirmação_delete_equipe.html'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'Membro da equipe deletado com sucesso com sucesso!')
        return super().post(request, *args, **kwargs)


class Cadastrar_Cliente(LoginRequiredMixin,View):
    template_name = 'posvendasapp/cadastro_att_cliente.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,{
            'cliente_form':Clienteforms(),
            'modo':'criação'
        })

    def post(self, request, *args, **kwargs):
        form_cliente=Clienteforms(request.POST,request.FILES)
        try:
            Main_services.cadastrar_cliente(form_cliente)
            return redirect('posvendasapp:tabela_cliente')
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
            'modo':'edição'

        })
    def post(self, request, *args, **kwargs):
        cliente = get_object_or_404(Clientes, pk=self.kwargs['pk'])
        form_cliente = Clienteforms( request.POST, request.FILES,instance=cliente)
        try:
            Main_services.atualizar_clientes(form_cliente)
            return redirect('posvendasapp:tabela_cliente')
        except ValidationError :
            print(form_cliente.errors)
            return render(request, self.template_name, {
                'cliente_form': form_cliente,
                'modo':'edição'

            })


class DeleteCliente(LoginRequiredMixin,DeleteView):
    model = Clientes
    success_url = reverse_lazy('posvendasapp:tabela_cliente')
    pk_url_kwarg = 'pk'
    template_name = 'posvendasapp/confirmação_delete_cliente.html'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'cliente deletado com sucesso com sucesso!')
        return super().post(request, *args, **kwargs)


class Cadastrar_Vendas(LoginRequiredMixin, View):
    template_name = 'posvendasapp/cadastro_vendas.html'

    def get(self, request, *args, **kwargs):
        cliente = Clientes.objects.get(pk=self.kwargs['pk'])
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
        cliente = Clientes.objects.get(pk=self.kwargs['pk'])
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
                'form_venda': form_venda,
                'form_produto_formset': produto_formset,
                'ocorrencia_formset': ocorrencia_formset,
                'errors': e,
                'modo': 'edição'
            })



class DeleteProduto(LoginRequiredMixin,DeleteView):
    model = Vendas
    success_url = reverse_lazy('posvendasapp:tabela_vendas')
    pk_url_kwarg = 'produto_pk'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'produto deletado com sucesso!')
        return super().post(request, *args, **kwargs)

class DeleteOcorrencia(LoginRequiredMixin,DeleteView):
    model = Vendas
    success_url = reverse_lazy('posvendasapp:tabela_vendas')
    pk_url_kwarg = 'ocorrencia_pk'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'Ocorrencia deletado com sucesso!')
        return super().post(request, *args, **kwargs)

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



class Listar_Staff(ListView):
    model = Equipe
    template_name = 'posvendasapp/tabela_equipe.html'
    context_object_name = 'equipe'
    paginate_by = 10

    def get_queryset(self):
        queryset = Equipe.objects.order_by('Usuario')
        cargo = self.request.GET.get('Cargo', 'None')
        if cargo != 'None' and cargo:
            queryset = queryset.filter(Cargo=cargo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cargos'] = Equipe.objects.values_list('Cargo', flat=True).distinct()
        return context


class Listar_Clientes(ListView):
    model = Clientes
    template_name = 'posvendasapp/tabela_clientes.html'
    context_object_name = 'cliente'
    paginate_by = 10

    def get_queryset(self):
        queryset = Clientes.objects.all()
        sort_param = self.request.GET.get('sort', '')

        # Aplica ordenação manual posterior com base no total
        if sort_param in ['valor_total', 'valor_total_asc']:
            queryset = list(queryset)
            queryset.sort(
                key=lambda cliente: cliente.valor_total_venda_do_cliente,
                reverse=(sort_param == 'valor_total')
            )
        elif sort_param == 'nome':
            queryset = queryset.order_by('Nome')
        elif sort_param == 'nome_desc':
            queryset = queryset.order_by('-Nome')
        else:
            queryset = queryset.order_by('-id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



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

        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        # Se for lista, paginar manualmente
        if isinstance(qs, list):
            paginator = Paginator(qs, self.paginate_by)
            page_number = self.request.GET.get('page') or 1
            page_obj = paginator.get_page(page_number)
            context['vendas'] = page_obj
            context['page_obj'] = page_obj
            context['paginator'] = paginator
            context['is_paginated'] = page_obj.has_other_pages()

        return context
class Delete_Venda(LoginRequiredMixin,DeleteView):
    model = Vendas
    success_url = reverse_lazy('posvendasapp:tabela_venda')
    pk_url_kwarg = 'pk'
    template_name = 'posvendasapp/confirmação_delete_venda.html'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'cliente deletado com sucesso com sucesso!')
        return super().post(request, *args, **kwargs)


class Listar_Produtos_Vendidos(LoginRequiredMixin, ListView):
    model = Produtos
    template_name = 'posvendasapp/tabela_produtos_vendidos.html'
    context_object_name = 'produtos'
    paginate_by = 10

    # def get_queryset(self):
    #     produtos_prefetch = Prefetch('produtos_vendidos')  # garantir prefetch
    #     qs = Vendas.objects.select_related('cliente', 'vendedor') \
    #         .prefetch_related(produtos_prefetch, 'ocorrencias_venda')
    #
    #     nome = self.request.GET.get('nome', '')
    #     valor = self.request.GET.get('valor', '')
    #     retorno = self.request.GET.get('retorno', '')
    #
    #     # Ordenação por nome
    #     if nome == 'az':
    #         return qs.order_by('cliente__Nome')
    #     elif nome == 'za':
    #         return qs.order_by('-cliente__Nome')
    #
    #     # Ordenação por valor total (manual)
    #     if valor in ['asc', 'dec']:
    #         lista = list(qs)  # Força avaliação com prefetch aplicado
    #         for venda in lista:
    #             list(venda.produtos_vendidos.all())  # Força carregar os produtos aqui
    #
    #         lista.sort(
    #             key=lambda v: v.valor_total_venda if v.valor_total_venda is not None else 0,
    #             reverse=(valor == 'dec')
    #         )
    #         return lista
    #
    #     # Ordenação por data de retorno (manual)
    #     if retorno in ['asc', 'dec']:
    #         lista = list(qs)
    #         lista.sort(
    #             key=lambda v: (v.Data_venda + timedelta(days=v.Previsao))
    #             if v.Data_venda and v.Previsao else date.min,
    #             reverse=(retorno == 'dec')
    #         )
    #         return lista
    #
    #     return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context