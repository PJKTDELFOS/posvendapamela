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
    password=forms.CharField(widget=forms.PasswordInput,max_length=255,required=True,label='Senha')

    password2 = forms.CharField(widget=forms.PasswordInput, max_length=255, required=True, label='Confirmação de Senha')

    def __init__(self,Usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Usuario = Usuario

    class Meta:
        model = User
        fields =['username','email','password','password2']


    def validate_unique(self):

        return



    def clean(self):
        cleaned_data = super().clean()
        validation_error_msg={}
        usuario_data=cleaned_data.get('username')#ficar de olho nesse, pode dar erro
        email_data = cleaned_data.get('email')
        password_data = cleaned_data.get('password')
        password2_data = cleaned_data.get('password2')

        usuario_db=User.objects.filter(username=usuario_data).first()
        email_db=User.objects.filter(email=email_data).first()


        erro_msg_user_exists='usuario ja existente'
        erro_msg_email_exists = 'email ja cadastrado'
        erro_msg_pass_match = 'senhas nao conferem'
        erro_msg_pass_len = 'tamanho minimo de senha: 6 ou mais caracteres'
        erro_msg_required='campo obrigatorio'

        print(self.cleaned_data)


        if self.Usuario:
            if self.Usuario:
                if usuario_db and usuario_db.id != self.Usuario.id:
                    validation_error_msg['username'] = erro_msg_user_exists
                if email_db and email_db.id != self.Usuario.id:
                    validation_error_msg['email'] = erro_msg_email_exists
            if password_data and password2_data:
                if password_data != password2_data:
                    validation_error_msg['password'] = erro_msg_pass_match
                    validation_error_msg['password2'] = erro_msg_pass_match
                if len(password_data) < 6:
                    validation_error_msg['password'] = erro_msg_pass_len
                if not re.search(r'[a-zA-Z]', password_data) or not re.search(r'\d', password_data):
                    validation_error_msg['password'] = "A senha deve conter pelo menos uma letra e um número."
            else:
                if not password_data:
                    validation_error_msg['password'] = erro_msg_required
                if not password2_data:
                    validation_error_msg['password2'] = erro_msg_required
        else:
            if usuario_db:
                validation_error_msg['username']=erro_msg_user_exists
            if email_db:
                validation_error_msg['email']=erro_msg_email_exists
            if not password_data:
                validation_error_msg['password']=erro_msg_required
            if not password2_data:
                validation_error_msg['password2']=erro_msg_required

            if password_data != password2_data:
                validation_error_msg['password'] = erro_msg_pass_match
                validation_error_msg['password2'] = erro_msg_pass_match

            if not re.search(r'[a-zA-Z]', password_data) or not re.search(r'\d', password_data):
                validation_error_msg['password'] = "A senha deve conter pelo menos uma letra e um número."

            if len(password_data) < 6:
                validation_error_msg['password'] = erro_msg_pass_len

        if validation_error_msg:
            raise(forms.ValidationError(validation_error_msg))





























