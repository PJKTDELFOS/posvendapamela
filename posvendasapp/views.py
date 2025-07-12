from posvendasapp.services.Services import Main_services
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404,redirect,render,HttpResponse
from django.views.generic.list import ListView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic.list import ListView,View
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404,redirect,render,HttpResponse
from . import models
from . import forms
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.db.models import Q
import os
from django.conf import settings
import shutil
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from.models import *
from .forms import *
from.vendasforms import *


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
    return render(request, 'posvendasapp/tabela_vendas.html')


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
    def get(self, request, equipe_id):
        equipe=get_object_or_404(Equipe,id=equipe_id)
        usuario=equipe.Usuario
        form_usuario=UsuarioForm(instance=usuario,Usuario=usuario)
        form_equipe=EquipeForm(instance=equipe)
            #aqui passa o contexto para os 2 formularios
        return render(request, self.template_name,{
            'form_usuario':form_usuario,
            'form_equipe':form_equipe,
            'modo': 'edição'})

    def post(self, request, equipe_id):
        equipe = get_object_or_404(Equipe, id=equipe_id)
        usuario = equipe.Usuario
        form_usuario = UsuarioForm(request.POST, instance=usuario, Usuario=usuario)
        form_equipe = EquipeForm(request.POST, instance=equipe)

        try:
            Main_services.Azualizar_Equipe(request.POST,request.POST,usuario,equipe)
            return redirect('posvendasapp:tabela_equipe')
        except ValidationError as e:
            errors=e.message_dict
            form_usuario.is_valid()
            form_equipe.is_valid()
            return render(request, self.template_name, {
                'form_usuario': form_usuario,
                'form_equipe':  form_equipe,
                'modo':'edição',
                'errors':errors,})



class DeleteEquipe(LoginRequiredMixin,DeleteView):
    model = Equipe
    success_url = reverse_lazy('posvendasapp:tabela_equipe')
    pk_url_kwarg = 'equipe_id'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'pagamento deletado com sucesso!')
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
                'modo': 'edição'

            })


class DeleteCliente(LoginRequiredMixin,DeleteView):
    model = Clientes
    success_url = reverse_lazy('posvendasapp:tabela_cliente')
    pk_url_kwarg = 'cliente_id'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'Cliente deletado com sucesso!')
        return super().post(request, *args, **kwargs)


class Cadastrar_Vendas(LoginRequiredMixin,View):
    template_name = 'posvendasapp/cadastrar_att_vendas.html'

    def get(self, request, *args, **kwargs):
        cliente=Clientes.objects.get(pk=self.kwargs['pk'])
        vendedor=request.user.equipe
        form_vendas=Vendaforms(cliente=cliente,vendedor=vendedor)
        produto_formset=ProdutoFormSet
        ocorrencia_formset=OcorrenciaFormSet(request=request)

        return render(request, self.template_name,{
            'form_vendas': form_vendas,
            'form_produto_formset': produto_formset,
            'ocorrencia_formset': ocorrencia_formset,
            'modo':'criação'
        })

    def post(self, request, *args, **kwargs):
        cliente = Clientes.objects.get(pk=self.kwargs['pk'])
        vendedor = request.user.equipe

        try:
            Main_services.cadastrar_venda(
                dados_venda=request.POST,
                dados_produto=request.POST,
                dados_ocorrencia=request.POST,
                cliente=cliente,
                vendedor=vendedor,
                request=request

            )
            return redirect('posvendasapp:tabela_cliente')#fazer a url para vendas correta
        except ValidationError as e:
            form_venda = Vendaforms(request.POST, cliente=cliente, vendedor=vendedor)
            formset_produto = ProdutoFormSet(request.POST)
            formset_ocorrencia = OcorrenciaFormSet(request.POST, request=request)

            return render(request, self.template_name, {
                'form_venda': form_venda,
                'formset_produto': formset_produto,
                'formset_ocorrencia': formset_ocorrencia,
                'errors': e,
            })


def teste_tabelaEquipe(request):
    print('Vai redirecionar para tabela_equipe')
    return render(request, 'posvendasapp/tabela_equipe.html')


def teste_tabela_cliente(request):
    print('Vai redirecionar para tabela_cliente')
    return render(request, 'posvendasapp/tabela_clientes.html')