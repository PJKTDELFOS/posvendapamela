import unicodedata
from django.template import Library
from openpyxl import load_workbook
from django import template
import os
from django.conf import settings
import unidecode
import pytz

register=Library()
@register.filter
def formata_preco(val):
    return f'R$:{val:.4f}'.replace('.',',')



import re

def valida_cpf(cpf):
    cpf = str(cpf)
    cpf = re.sub(r'[^0-9]', '', cpf)

    if not cpf or len(cpf) != 11:
        return False

    novo_cpf = cpf[:-2]                 # Elimina os dois últimos digitos do CPF
    reverso = 10                        # Contador reverso
    total = 0

    # Loop do CPF
    for index in range(19):
        if index > 8:                   # Primeiro índice vai de 0 a 9,
            index -= 9                  # São os 9 primeiros digitos do CPF

        total += int(novo_cpf[index]) * reverso  # Valor total da multiplicação

        reverso -= 1                    # Decrementa o contador reverso
        if reverso < 2:
            reverso = 11
            d = 11 - (total % 11)

            if d > 9:                   # Se o digito for > que 9 o valor é 0
                d = 0
            total = 0                   # Zera o total
            novo_cpf += str(d)          # Concatena o digito gerado no novo cpf

    # Evita sequencias. Ex.: 11111111111, 00000000000...
    sequencia = novo_cpf == str(novo_cpf[0]) * len(cpf)

    # Descobri que sequências avaliavam como verdadeiro, então também
    # adicionei essa checagem aqui
    if cpf == novo_cpf and not sequencia:
        return True
    else:
        return False

import os

def sanitize_name(value):
    """Remove caracteres especiais e substitui espaços por underscores."""
    return ''.join(e if e.isalnum() or e == '_' else '_' for e in value.replace(' ', '_'))

def cliente_upload_path(instance, filename):
    pasta_cliente_nome =f'{instance.id}-{sanitize_name(instance.Nome)}'


    return os.path.join(f'Clientes/{pasta_cliente_nome}/', filename)

def processo_upload_path(instance, filename):
    processo_nome = (f'{instance.pk or "novo"}')

    tipo_documento = sanitize_name(instance.tipo_documento)

    return os.path.join(f'processos/{processo_nome}/{tipo_documento}', filename)

def contrato_upload_path(instance, filename):
    processo_nome = (f'{instance.processo.pk or "novo"}')
    contrato_nome = (f'{instance.pk or "novo"}')
    tipo_documento = sanitize_name(instance.tipo_documento)

    return os.path.join(f'processos/{processo_nome}/contratos/{contrato_nome}/{tipo_documento}', filename)

def pedido_upload_path(instance, filename):
    processo_nome = (f'{instance.contrato.processo.pk or "novo"}')

    contrato_nome = (f'{instance.contrato.pk or "novo"}')

    pedido_nome = (f'{instance.pk or "novo"}')

    tipo_documento = sanitize_name(instance.tipo_documento)

    return os.path.join(
       'processos',processo_nome,'contratos',
        contrato_nome,'pedidos',pedido_nome,tipo_documento,filename
    )

# settings.MEDIA_ROOT, 'processos', processo_nome, 'contratos', contrato_nome, 'pedidos', pedido_nome, tipo_documento, filename

def docs_rh_load_path(instance, filename):
    funcionario_arquivos = (f'{instance.cpf or "novo"}')
    tipo_documento = sanitize_name(instance.tipo_documento)

    return os.path.join(f'rh/{funcionario_arquivos}/{tipo_documento}', filename)


def docs_finan_load_path(instance,filename):
    vencimento = instance.vencimento
    subpasta=instance.pk
    arquivo=instance.documentos
    filename=unidecode.unidecode(filename.replace(" ", "_"))
    return os.path.join(f'financeiro/pagamento/{vencimento}/{subpasta}/',filename )

def docs_finan_load_path_rcbm(instance,filename):
    data_pgto = instance.data_pgto
    subpasta=instance.origem
    filename=unidecode.unidecode(filename.replace(" ", "_"))
    return os.path.join(f'financeiro/recebimento/{data_pgto}/{subpasta}/',filename )

def documentos_load_path(instance,filename):
    documento = instance.documento
    setor=instance.pedido_origem
    tipo=instance.tipo_documento
    filename=unidecode.unidecode(filename.replace(" ", "_"))
    return os.path.join(f'documentos/{setor}/{tipo}/{documento}/',filename )


def documentos_frota_load_path(instance,filename):
    placa=instance.placa
    ativo = instance.Ativo
    nome_ativo=f'{ativo}-{placa}'
    tipo_ativo=instance.tipo.tipo_de_ativo
    filename=unidecode.unidecode(filename.replace(" ", "_"))
    return os.path.join(f'operacional/frota/{tipo_ativo}/{nome_ativo}/',filename )

def documentos_manutencao_frota_load_path(instance,filename):
    placa=instance.Ativo_em_manutencao.placa
    ativo = instance.Ativo_em_manutencao.Ativo
    nome_ativo=f'{ativo}-{placa}'
    tipo_ativo=instance.Ativo_em_manutencao.tipo.tipo_de_ativo
    operacao=instance.operacao
    ordem=instance.pk
    filename=unidecode.unidecode(filename.replace(" ", "_"))
    return os.path.join(f'operacional/frota/{tipo_ativo}/{nome_ativo}/manutencao/{operacao}/Ordem nº{ordem}/',filename )

def documentos_amoxarifado_load_path(instance,filename):
    tipo=instance.item.tipo
    nome=instance.item.nome
    lote=instance.nota
    filename=unidecode.unidecode(filename.replace(" ", "_"))
    return os.path.join(f'operacional/almoxarifado/'
                        f'{tipo}/{nome}/lotes/{lote}/',filename )


def planilha_upload_path(instance, filename):
    processo_nome = (f'{instance.contrato.processo.pk or "novo"}')

    contrato_nome = (f'{instance.contrato.pk or "novo"}')

    pedido_nome = (f'{instance.pk or "novo"}')

    tipo_documento = 'PEDIDO'

    return os.path.join(
        settings.MEDIA_ROOT,'processos',processo_nome,'contratos',
        contrato_nome,'pedidos',pedido_nome,tipo_documento,filename
    )

# ser operacional/frota/ativo/tipo_ativo/nome_ativo/manutencao/tipo/ordem/filename
def criar_planilha(instance):
    template_form = os.path.join(settings.BASE_DIR, 'processos/templates/planilhas/modelo_pedido.xlsx')
    name = f'Pedido-{str(instance.numero)}-{str(instance.contratante)}'
    save_path = planilha_upload_path(instance, f'{name}.xlsx')
    if os.path.exists(save_path):
        print(f"Atualizando planilha existente em: {save_path}")
        print(save_path, 'atualizando a planilha ')
    else:
        try:
            workbook = load_workbook(filename=template_form)
            worksheet = workbook['sheet']
            br_tz = pytz.timezone('America/Sao_Paulo')
            data_origem = str(instance.data_origem) if instance.data_origem else ''
            data_entrega = str(instance.data_entrega) if instance.data_entrega else ''
            data_hora_att = instance.data_hora_att.astimezone(br_tz).strftime(
                '%d/%m/%Y %H:%M:%S') if instance.data_hora_att else ''
            recebimento_empenho = str(instance.recebimento_empenho) if instance.recebimento_empenho else ''
            worksheet['I9'] = instance.numero
            worksheet['I10'] = data_origem  # criação
            worksheet['I12'] = instance.cnpj_contratante
            worksheet['B12'] = instance.contratante
            worksheet['A15'] = str(instance.contrato)
            worksheet['C15'] = instance.empenho
            worksheet['D15'] = instance.ordem_fornecimento
            worksheet['E15'] = recebimento_empenho  # recebimento empenho
            worksheet['G15'] = instance.contato
            worksheet['H15'] = instance.telefone
            worksheet['I15'] = instance.email
            worksheet['D17'] = instance.objeto
            worksheet['B16'] = data_entrega
            worksheet['D16'] = instance.endereco_entrega
            worksheet['A21'] = instance.unidade_fornecimento
            worksheet['B21'] = instance.qtde
            worksheet['A23'] = instance.observacoes
            worksheet['B51'] = instance.coordenador
            worksheet['I11'] = data_hora_att  # ultima modifica
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            workbook.save(filename=save_path)
            print(save_path, 'caminho da planilha do models ')
            print(f'planilha salva como {name}.xlsx')
        except Exception as e:
            name = f'Pedido_nº{instance.numero}_contrato:{instance.contrato}'
            print(f"Erro na planilha: {e}, pedido {name} nao  se nao puder fazer a planilha ")



class CalculadoraCustoTotal:
    def __init__(self, instance):
        self.instance=instance

    def calcular_total_alocado(self):
        return sum(
            recurso_alocado.custo_total() for
            recurso_alocado in
            self.instance.recurso_alocados.all())




# def docs_finan_load_path(instance, filename):
#     funcionario_arquivos = (f'{instance.pk or "novo"}-{sanitize_name(instance.nome)}'
#                      f'-{sanitize_name(instance.cpf)}')
#     tipo_documento = sanitize_name(instance.tipo_documento)
#
#     return os.path.join(f'rh/{funcionario_arquivos}/{tipo_documento}', filename)


#fazer upload paths especificos e trocar o nome da pasta