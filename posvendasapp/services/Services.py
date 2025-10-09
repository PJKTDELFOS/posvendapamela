from posvendasapp.forms import EquipeForm,UsuarioForm
from posvendasapp.vendasforms import *
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from utils.tools_utils import *
import hashlib


class Main_services:

    @staticmethod
    def criar_equipe(dados_usuario,dados_equipe,request_user=None):
        form_usuario=UsuarioForm(dados_usuario,Usuario=None)
        form_equipe=EquipeForm(dados_equipe)

        if not form_usuario.is_valid():
            raise ValidationError(form_usuario.errors)

        if not form_equipe.is_valid():
            raise ValidationError(form_equipe.errors)


        user=form_usuario.save(commit=False)
        user.set_password(form_usuario.cleaned_data['password'])
        user.is_active=False
        user.save()

        equipe=form_equipe.save(commit=False)
        equipe.Usuario=user

        equipe.save()
        if request_user:
            registrar_log(request_user,'cadastrou membro',equipe)
        return equipe


    @staticmethod
    def atualizar_equipe(form_usuario,form_equipe,request_user=None):

        if not form_usuario.is_valid():
            raise ValidationError(form_usuario.errors)
        if not form_equipe.is_valid():
            raise ValidationError(form_equipe.errors)

        user = form_usuario.save(commit=False)
        nova_senha = form_usuario.cleaned_data.get('password')
        if nova_senha:
            user.set_password(nova_senha)
        user.save()

        equipe = form_equipe.save(commit=False)
        equipe.Usuario = user
        equipe.save()

        if request_user:
            registrar_log(request_user, 'atualizou membro', equipe)

        return equipe

    @staticmethod
    def cadastrar_cliente(form):
        if not form.is_valid():
            raise ValidationError(form.errors)
        cliente=form.save()
        return cliente

    @staticmethod
    def atualizar_clientes(form):
        if not form.is_valid():
            raise ValidationError(form.errors)
        cliente=form.save()
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
        ocorrencia_formset.request = request

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
        if not termo:
            return queryset.none()
        termo_limpo_num = ''.join(filter(str.isdigit, termo))
        hash_num = hashlib.sha256(termo_limpo_num.encode('utf-8')).hexdigest()
        hash_email = hashlib.sha256(termo.lower().encode('utf-8')).hexdigest()
        q_hash_match=Q()
        if 'cpf_hash' in campos:
            q_hash_match |= Q(cpf_hash__iexact=hash_num)
        if 'tel_contato_hash' in campos:
            q_hash_match |= Q(tel_contato_hash__iexact=hash_num)
        if 'email_hash' in campos:
            q_hash_match |= Q(email_hash__iexact=hash_email)
        q_text_match=Q()
        palavras = termo.split()
        for palavra in palavras:
            q_or_palavra=Q()
            for campo in campos:
                if campo not in['cpf_hash','tel_contato_hash','email_hash']:
                    q_or_palavra |= Q(
                        **{f'{campo}__icontains':palavra}
                    )

            if q_text_match:
                q_text_match &= q_or_palavra
            else:
                q_text_match = q_or_palavra
        q_final = q_hash_match | q_text_match
        return queryset.filter(q_final).distinct()






















