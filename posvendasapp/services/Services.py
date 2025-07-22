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
            raise ValidationError(form_usuario.errors)

        if not form_equipe.is_valid():
            raise ValidationError(form_equipe.errors)


        user=form_usuario.save(commit=False)
        user.set_password(form_usuario.cleaned_data['password'])
        user.save()

        equipe=form_equipe.save(commit=False)
        equipe.Usuario=user
        equipe.save()
        return equipe


    @staticmethod
    def atualizar_equipe(form_usuario,form_equipe):

        if not form_usuario.is_valid():
            raise ValidationError(form_usuario.errors)

        if not form_equipe.is_valid():
            raise ValidationError(form_equipe.errors)

        user=form_usuario.save(commit=False)
        nova_senha = form_usuario.cleaned_data['password']
        if nova_senha:
            user.set_password(nova_senha)

        usuario=form_usuario.save(commit=False)
        usuario.Usuario=user
        usuario.save()

        equipe = form_equipe.save(commit=False)
        equipe.Usuario = user
        equipe.save()
        return equipe

    @staticmethod
    def cadastrar_cliente(form):
        if not form.is_valid():
            raise ValidationError(form.errors)
        cliente=form.save(commit=False)
        cliente.save()
        return cliente

    @staticmethod
    def atualizar_clientes(form):
        if not form.is_valid():
            raise ValidationError(form.errors)
        cliente=form.save(commit=False)
        cliente.save()
        return cliente

    @staticmethod
    def cadastrar_venda(dados_venda, dados_produto, dados_ocorrencia, cliente, vendedor, request):
        vendas_form = Vendaforms(dados_venda, cliente=cliente, vendedor=vendedor)
        if not vendas_form.is_valid():
            raise ValidationError(vendas_form.errors)

        venda = vendas_form.save(commit=False)
        venda.cliente = cliente
        venda.vendedor = vendedor
        venda.save()  # Precisa salvar antes de usar como instance nos formsets

        produto_formset = ProdutoFormSet(data=dados_produto, instance=venda, prefix='produtos')
        ocorrencia_formset = OcorrenciaFormSet(data=dados_ocorrencia, instance=venda, prefix='ocorrencias')
        ocorrencia_formset.request = request  # ✅ Corrigido aqui

        if not produto_formset.is_valid():
            print("Erros no formset de produtos:", produto_formset.errors)
            raise ValidationError(produto_formset.errors)

        if not ocorrencia_formset.is_valid():
            raise ValidationError(ocorrencia_formset.errors)

        with transaction.atomic():
            produto_formset.save()
            ocorrencia_formset.save()

        return venda

    @staticmethod
    def atualizar_venda(dados_venda,dados_produto,dados_ocorrencia,venda,cliente,vendedor,request=None):
        vendas_form=Vendaforms(dados_venda,instance=venda,cliente=cliente,vendedor=vendedor)
        produto_formset=ProdutoFormSet(dados_produto,instance=venda,prefix='produtos')
        ocorrencia_formset = OcorrenciaFormSet(dados_ocorrencia, instance=venda, prefix='ocorrencias')
        ocorrencia_formset.request = request

        if not vendas_form.is_valid():
            print('erro na venda service',vendas_form.errors)
            raise ValidationError(vendas_form.errors)
        if not produto_formset.is_valid():
            print('erro no produto service',produto_formset.errors)
            raise ValidationError(produto_formset.errors)
        if not ocorrencia_formset.is_valid():
            print('erro na ocorrencia service',ocorrencia_formset.errors)
            print(ocorrencia_formset.data)
            raise ValidationError(ocorrencia_formset.errors)

        with transaction.atomic():
            venda=vendas_form.save(commit=False)
            venda.cliente=cliente
            venda.vendedor=vendedor
            venda.save()
            produto_formset.save()
            ocorrencia_formset.save()

        return venda

    @staticmethod
    def busca_centralizada(queryset, termo, campos):
        from django.db.models import Q

        palavras = termo.split()
        q = Q()
        for palavra in palavras:
            q_palavra = Q()
            for campo in campos:
                q_palavra |= Q(**{f"{campo}__icontains": palavra})
            q &= q_palavra  # usa AND entre palavras, para pegar todas
        return queryset.filter(q).distinct()
















