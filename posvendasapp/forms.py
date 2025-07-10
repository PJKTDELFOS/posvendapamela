from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Equipe
import re
from django.core.exceptions import ValidationError


class EquipeForm(forms.ModelForm):
    Cargo = forms.ChoiceField(required=True
                              , choices=Equipe._meta.get_field('Cargo').choices)
    class Meta:
        model = Equipe
        exclude = ('Usuario',)

class UsuarioForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label='Usuário')
    password = forms.CharField(widget=forms.PasswordInput, max_length=255, required=True, label='Senha')
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=255, required=True, label='Confirmação de Senha')

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        self.Usuario = kwargs.pop('Usuario', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['password2'].required = False

    def clean(self):
        cleaned_data = super().clean()
        usuario_data = cleaned_data.get('username')
        email_data = cleaned_data.get('email')
        password_data = cleaned_data.get('password')
        password2_data = cleaned_data.get('password2')

        usuario_db = User.objects.filter(username=usuario_data).first() if usuario_data else None
        email_db = User.objects.filter(email=email_data).first() if email_data else None

        # Validação de duplicidade de usuário/email
        if self.Usuario:
            if usuario_db and usuario_db.id != self.Usuario.id:
                self.add_error('username', 'usuario ja existente')
            if email_db and email_db.id != self.Usuario.id:
                self.add_error('email', 'email ja cadastrado')
        else:
            if usuario_db:
                self.add_error('username', 'usuario ja existente')
            if email_db:
                self.add_error('email', 'email ja cadastrado')

        # Validação da senha
        if not self.instance.pk:  # Criação
            if not password_data:
                self.add_error('password', 'campo obrigatorio')
            if not password2_data:
                self.add_error('password2', 'campo obrigatorio')
            if password_data and password2_data and password_data != password2_data:
                self.add_error('password', 'senhas nao conferem')
                self.add_error('password2', 'senhas nao conferem')

        else:  # Edição
            if password_data or password2_data:
                if password_data != password2_data:
                    self.add_error('password', 'senhas nao conferem')
                    self.add_error('password2', 'senhas nao conferem')

        # senha segura
        if password_data:
            if len(password_data) < 6:
                self.add_error('password', 'tamanho minimo de senha: 6 ou mais caracteres')
            if not re.search(r'[a-zA-Z]', password_data) or not re.search(r'\d', password_data):
                self.add_error('password', 'A senha deve conter pelo menos uma letra e um número.')

        return cleaned_data


























