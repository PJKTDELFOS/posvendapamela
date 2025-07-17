from django import forms
from .models import Vendas,Clientes,Produtos,Ocorrencia
from django.forms import inlineformset_factory,BaseInlineFormSet,modelformset_factory





class Clienteforms(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = '__all__'
        labels={
            'Nome':'Cliente',
            'contato':'Contato do cliente',
            'Arquivos':'Documentos',
        }

        widgets={
            'Nome':forms.TextInput(attrs={'class':'form-control'}),
            'contato':forms.TextInput(attrs={'class':'form-control'}),
            'Arquivos':forms.FileInput(attrs={'class':'form-control'}),
        }


class Vendaforms(forms.ModelForm):
    #cliente para qual foi feita a venda
    cliente_db=forms.CharField(
        label='Cliente',
        required=False,
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        )
    )
    #vendedor que fez a venda
    vendedor_db=forms.CharField(
        label='Vendedor',
        required=False,
        widget=forms.TextInput(
            attrs={'readonly': 'readonly'}
        )
    )
    class Meta:
        model = Vendas
        exclude=['cliente','vendedor']
        widgets={
            'Data_venda':forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'}),
            'Previsao':forms.NumberInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        cliente_obj=kwargs.pop('cliente',None)
        vendedor_obj=kwargs.pop('vendedor',None)
        super().__init__(*args, **kwargs)

        #cliente
        if cliente_obj:
            self.fields['cliente_db'].initial=cliente_obj.Nome
            self.instance.cliente=cliente_obj
            self.fields['cliente_db'].label='Cliente'
        else:
            self.instance.cliente=None
            self.fields['cliente_db'].initial='Nenhum cliente localizado'

        # vendedor
        if vendedor_obj:
            self.fields['vendedor_db'].initial=vendedor_obj.Usuario.username
            self.instance.vendedor=vendedor_obj
            self.fields['vendedor_db'].label='Vendedor'
        else:
            self.instance.vendedor=None
            self.fields['vendedor_db'].initial='Nenhum vendedor localizado'

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.cliente:
            self.add_error(None, ' falta cliente')
        if not self.instance.vendedor:
            self.add_error(None, ' falta vendedor')
        return cleaned_data

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produtos
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Valor_venda'].required = True

class OcorrenciaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Ocorrencia
        exclude=['vendedor']

class ProdutoFormSetCustom(BaseInlineFormSet):
    def clean(self):
        super().clean()
        produtos_na_venda = 0

        for i, form in enumerate(self.forms):
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                produtos_na_venda += 1

                valor = form.cleaned_data.get('Valor_venda')
                print(f"[DEBUG] Produto {i}: Valor_venda = {valor}")

                if valor is not None and valor <= 0:
                    form.add_error('Valor_venda', 'O valor do produto deve ser maior que zero')

        if produtos_na_venda == 0:
            raise forms.ValidationError('Deve haver pelo menos um produto vendido')

    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        obj.venda = self.instance
        obj.save()
        return obj



class OcorrenciaInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        # Passa o request para o form
        form = super()._construct_form(i, **kwargs)
        form.request = self.request
        return form

    def save_new(self, form, commit=True):
        # Cria a instância sem salvar ainda
        obj = form.save(commit=False)
        obj.venda = self.instance

        # Associa vendedor à equipe do usuário logado
        if self.request and hasattr(self.request.user, 'equipe'):
            obj.vendedor = self.request.user.equipe

        if commit:
            obj.save()
        return obj


ProdutoFormSet = inlineformset_factory(
    Vendas,Produtos,
    fields='__all__',
    extra=0,can_delete=True,
    form=ProdutoForm,
    formset=ProdutoFormSetCustom,
)

OcorrenciaFormSet = inlineformset_factory(
    Vendas, Ocorrencia,
    form=OcorrenciaForm,
    formset=OcorrenciaInlineFormSet,
    extra=0, can_delete=True
)



















