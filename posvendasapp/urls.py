"""
URL configuration for posvendas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .import views


app_name = 'posvendasapp'

urlpatterns = [
    path('login', views.Login.as_view(), name='login_sistema'),
    path('logout', views.Logout.as_view(),name='logout'),
     path('', views.testelogin, name='menuinicial'),


    #tabelas
    path('tabela_equipe', views.teste_tabelaEquipe, name='tabela_equipe'),
    path('tabela_cliente', views.teste_tabela_cliente, name='tabela_cliente'),

    #cadastro
    path('cadastrar_equipe', views.CadastrarEquipe.as_view(), name='cadastrar_equipe'),
    path('cadastrar_cliente', views.Cadastrar_Cliente.as_view(), name='cadastrar_cliente'),




    #atualização



    #deletar



    #visualizar registros individuais

]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

