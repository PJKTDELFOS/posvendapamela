from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from utils import tools_utils
from datetime import timedelta,date
import os
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
# Create your models here.



class Equipe(models.Model):
    Usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                                   related_name='equipe',verbose_name='Usuario',blank=False,null=False,
                                   max_length=255)
    Cargo = models.CharField(default=None, max_length=60, choices=(
        ('Vendedor', 'Vendedor'),
        ('Gerente', 'Gerencia'),
        ('Supervisor', 'Supervisão'),
        ('Direção', 'Direção'),  ),null=False, blank=False)

    def __str__(self):
        return self.Usuario.username

    class Meta:
        verbose_name = 'Membro'
        verbose_name_plural = 'Equipe'


class Clientes(models.Model):
    Nome=models.CharField(default=None, max_length=254,blank=False,null=False,verbose_name='Nome')
    tel_contato=models.CharField(default=None, max_length=255,
                                 blank=False,null=False,verbose_name='telefone de contato',validators=[
            RegexValidator(regex=r'^\d{10,11}$',
                           message='digite somente numeros',
                           code='Numero Invalido')#terminar a validação via regex
        ]
                                 )
    email=models.CharField(default=None, max_length=255,blank=True,null=True,verbose_name='Email')
    cpf = models.CharField(max_length=14,blank=False,null=False,verbose_name='CPF',unique=True, )
    aniversario=models.DateField(default=None, blank=True, null=True, verbose_name='Data de Aniversario')
    Arquivos=models.FileField(upload_to=tools_utils.cliente_upload_path,blank=True,null=True,verbose_name='Arquivos')

    def __str__(self):
        return self.Nome

    def nome_arquivo(self):
        if self.Arquivos:
            return os.path.basename(self.Arquivos.name)
        return

    def clean(self):
        error_messages={}
        cpf_valido=tools_utils.valida_cpf(self.cpf)
        if not cpf_valido:
            error_messages['cpf']='digite um cpf valido'
        if error_messages:
            raise ValidationError(error_messages)



    @property
    def valor_total_venda_do_cliente(self):
        valor_total = sum(venda.valor_total_venda or 0 for venda in self.Vendas.all())
        return valor_total

    def valor_total_venda_do_cliente_formatada(self):
        return self.valor_total_venda_do_cliente
    valor_total_venda_do_cliente_formatada.short_description = 'valor total de vendas ao cliente '

    def save(self, *args, **kwargs):
        is_new=self.pk is None
        if is_new:
            temp_doc=self.Arquivos
            self.Arquivos=None
            super().save(*args, **kwargs)
            self.Arquivos = temp_doc
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

class Vendas(models.Model):
    cliente=models.ForeignKey(Clientes,on_delete=models.CASCADE,
                              verbose_name='Cliente',blank=False,null=False,related_name='Vendas')
    Data_venda = models.DateField(default=None, blank=False, null=False, verbose_name='Data de venda')
    Previsao = models.IntegerField(blank=True, null=True, verbose_name='Previsao')
    vendedor=models.ForeignKey(Equipe,on_delete=models.CASCADE,related_name='Vendedor',verbose_name='Vendedor',blank=False,null=False,)
    sequencia_venda=models.CharField(max_length=12,blank=True, null=True, verbose_name='Sequencia de venda',default=None,unique=True)

    def __str__(self):
        cliente=self.cliente
        return cliente.Nome
    @property
    def previsao_de_retorno(self):
        if isinstance(self.Data_venda, date) and isinstance(self.Previsao, int):
            data_retorno = self.Data_venda + timedelta(days=self.Previsao)
            return data_retorno.strftime('%d/%m/%Y')
        return 'Previsao nao definida'

    def previsao_retorno_formatada(self):
        return f'{self.previsao_de_retorno} dias'
    previsao_retorno_formatada.short_description = 'Previsao retorno formatada'

    @property
    def previsao_data(self):
        if isinstance(self.Data_venda, date) and isinstance(self.Previsao, int):
            return self.Data_venda + timedelta(days=self.Previsao)
        return None

    @property
    def valor_total_venda(self):
        valor_total=sum(v.Valor_venda or 0 for v in self.produtos_vendidos.all())
        return valor_total
    def valor_total_venda_formatada(self):
        return self.valor_total_venda
    valor_total_venda_formatada.short_description = 'valor total de vendas '

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'


class Produtos(models.Model):
    venda=models.ForeignKey(Vendas,on_delete=models.CASCADE,verbose_name='Venda',related_name='produtos_vendidos')
    Produto = models.CharField(default=None, max_length=255, blank=False, null=False, verbose_name='Produto')
    tipo=models.CharField(default=None, max_length=60, choices=(
        ('Contato-diaria', 'Contato-diaria'),
        ('Contato-Quinzenal', 'Contato-Quinzenal'),
        ('Solar', 'Armação'),
        ('Receituario', 'Armação'),
        ('Multifocal', 'Lente Oftalmica'),
        ('Visão simples', 'Lente oftalmica'),

    ), null=False, blank=False)
    Valor_venda = models.DecimalField(default=None, blank=False, null=False, verbose_name='Valor de venda',
                                      decimal_places=2,max_digits=9 )
    valor_produto_sem_desconto = models.DecimalField(default=None,
                                                     blank=False, null=False, verbose_name='Valor original do produto',
                                                     decimal_places=2, max_digits=9)


    @property
    def desconto(self):
        if self.valor_produto_sem_desconto:
            valor_descontado=self.valor_produto_sem_desconto-self.Valor_venda
            desconto=(valor_descontado/self.valor_produto_sem_desconto)*100
            return f'{desconto:.2f}% '
        return"0%"

    def desconto_formatada(self):
        return self.desconto
    desconto_formatada.short_description = 'Desconto '


    def __str__(self):
        return self.Produto


    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'



class Ocorrencia(models.Model):
    venda=models.ForeignKey(Vendas,on_delete=models.CASCADE,verbose_name='Venda',related_name='ocorrencias_venda')
    vendedor=models.ForeignKey(Equipe,on_delete=models.CASCADE,related_name='Vendedor_ocorrencia',
                               verbose_name='Vendedor',blank=False,null=False,)
    titulo_ocorrencia=models.CharField(default=None, max_length=255, blank=False, null=False, verbose_name='Titulo')
    tipo_ocorrencia=models.CharField(default=None, max_length=60, choices=(
        ('Troca-compra errada', 'Troca compra Errada'),
        ('Troca-Garantia', 'Troca-Garantia'),
        ('Atualização', 'Atualização'),
        ('Manutenção', 'Manutenção')
        ), null=False, blank=False)

    data_correncia=models.DateField(auto_now_add=True, blank=False, null=False, verbose_name='Data de correncia')
    ocorrencia=models.TextField(default='Descreva a ocorrencia',
                                blank=True, null=True, verbose_name='Ocorrencia',max_length=5000)

    def __str__(self):
        return f' venda :{self.venda.pk}- Ocorrenia:{self.titulo_ocorrencia} '


    class Meta:
        verbose_name = 'Ocorrencia'
        verbose_name_plural = 'Ocorrencias'





class logAcao(models.Model):
    usuario=models.ForeignKey(User,on_delete=models.SET_NULL,verbose_name='Usuario',null=True,)
    acao=models.CharField(default=None, max_length=255, blank=False, null=False, verbose_name='Acao')

    content_type=models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id=models.PositiveIntegerField()
    objeto=GenericForeignKey('content_type', 'object_id')
    data_hora=models.DateTimeField(auto_now_add=True,verbose_name='Data e Hora')

    class Meta:
        verbose_name = 'Log Acao'
        verbose_name_plural = 'Log de Acoes'
        ordering=('-data_hora',)

    def __str__(self):
        return f"{self.data_hora} - {self.usuario} - {self.acao} - {self.objeto}"











