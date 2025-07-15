from posvendasapp.forms import EquipeForm,UsuarioForm
from posvendasapp.vendasforms import *
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q


class Main_services:

    @staticmethod
    def criar_equipe(dados_usuario,dados_equipe):
        form_usuario=UsuarioForm(dados_usuario,Usuario=None)
        form_equipe=EquipeForm(dados_equipe)

        if not form_usuario.is_valid():
            raise ValidationError({'usuario':form_usuario.errors})

        if not form_equipe.is_valid():
            raise ValidationError({'equipe':form_equipe.errors})


        user=form_usuario.save(commit=False)
        user.set_password(form_usuario.cleaned_data['password'])
        user.save()

        equipe=form_equipe.save(commit=False)
        equipe.Usuario=user
        equipe.save()
        return equipe


    @staticmethod
    def Azualizar_Equipe(dados_usuario,dados_equipe,usuario,equipe):
        form_usuario=UsuarioForm(dados_usuario,instance=usuario,Usuario=None)
        form_equipe=EquipeForm(dados_equipe,instance=equipe)

        if not form_usuario.is_valid():
            raise ValidationError({'usuario': form_usuario.errors})

        if not form_equipe.is_valid():
            raise ValidationError({'equipe': form_equipe.errors})

        user=form_usuario.save(commit=False)
        nova_senha = form_usuario.cleaned_data['password']
        if nova_senha:
            user.set_password(nova_senha)

        equipe = form_equipe.save(commit=False)
        equipe.Usuario = user
        equipe.save()
        return equipe

    @staticmethod
    def cadastrar_cliente(form):
        if not form.is_valid():
            raise ValidationError("Formulário inválido")
        cliente=form.save(commit=False)
        cliente.save()
        return cliente

    @staticmethod
    def atualizar_clientes(form):
        if not form.is_valid():
            raise ValidationError("Formulário inválido")
        cliente=form.save(commit=False)
        cliente.save()
        return cliente

    @staticmethod
    def cadastrar_venda(dados_venda, dados_produto, dados_ocorrencia, cliente, vendedor, request):
        vendas_form = Vendaforms(dados_venda, cliente=cliente, vendedor=vendedor)
        if not vendas_form.is_valid():
            raise ValidationError({'form': vendas_form.errors})

        venda = vendas_form.save(commit=False)
        venda.cliente = cliente
        venda.vendedor = vendedor

        produto_formset = ProdutoFormSet(data=dados_produto, instance=venda)
        ocorrencia_formset = OcorrenciaFormSet(data=dados_ocorrencia, instance=venda)
        ocorrencia_formset.request = request  # atribui request aqui, não no construtor

        if not produto_formset.is_valid():
            raise ValidationError({'form': produto_formset.errors})
        if not ocorrencia_formset.is_valid():
            raise ValidationError({'form': ocorrencia_formset.errors})

        with transaction.atomic():
            venda.save()
            produto_formset.save()
            ocorrencia_formset.save()

        return venda

    @staticmethod
    def atualizar_venda(dados_venda,dados_produto,dados_ocorrencia,venda,cliente,vendedor,request=None):
        vendas_form=Vendaforms(dados_venda,instance=venda,cliente=cliente,vendedor=vendedor)
        produto_formset=ProdutoFormSet(dados_produto,instance=venda)
        ocorrencia_formset=OcorrenciaFormSet(dados_ocorrencia,instance=venda,request=request)
        if not vendas_form.is_valid():
            raise ValidationError({'form':vendas_form.errors})
        if not produto_formset:
            raise ValidationError({'form':produto_formset.errors})
        if not ocorrencia_formset:
            raise ValidationError({'form':ocorrencia_formset.errors})

        with transaction.atomic():
            venda=vendas_form.save(commit=False)
            venda.cliente=cliente
            venda.vendedor=vendedor
            venda.save()
            produto_formset.save()
            ocorrencia_formset.save()

        return venda

    @staticmethod
    def busca_centralizada(queryset,termo,campos):
        q=Q()
        for campo in campos:
            q |= Q(**{f"{campo}__icontains": termo})
        return queryset.filter(q)
















