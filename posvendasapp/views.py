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
    return render(request, 'posvendasapp/vendas.html')


class CadastrarEquipe(View):
    template_name = 'posvendasapp/cadastro_att_equipe.html'
    def get(self, request, *args, **kwargs):
        form_usuario=UsuarioForm()
        form_equipe=EquipeForm()
            #aqui passa o contexto para os 2 formularios
        return render(request, self.template_name,{
            'form_usuario':form_usuario,
            'form_equipe':form_equipe,
        })

    def post(self, request, *args, **kwargs):
        form_usuario = UsuarioForm(request.POST,Usuario=None)
        form_equipe = EquipeForm(request.POST)

        print("POST recebido:", request.POST)

        usuario_valido = form_usuario.is_valid()
        equipe_valida = form_equipe.is_valid()

        if not usuario_valido:
            print('esta com algum erro no usuario')
            print('Erros Usuário:', form_usuario.errors.as_data())

        if not equipe_valida:
            print('esta com algum erro na equipe')
            print('Erros Equipe:', form_equipe.errors.as_json())

        if usuario_valido and equipe_valida:
            user = form_usuario.save(commit=False)
            user.set_password(form_usuario.cleaned_data['password'])
            user.save()

            equipe = form_equipe.save(commit=False)
            equipe.Usuario = user
            equipe.save()

            print("Redirecionando para tabela_equipe")
            return redirect('posvendasapp:tabela_equipe')

        return render(request, self.template_name, {
            'form_usuario': form_usuario,
            'form_equipe': form_equipe,
        })


def teste_tabelaEquipe(request):
    print('Vai redirecionar para tabela_equipe')
    return render(request, 'posvendasapp/tabela_equipe.html')
