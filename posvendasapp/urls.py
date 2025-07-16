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

    path('busca', views.Busca.as_view(), name='busca_dinamica'),


    #equipe
    path('tabela_equipe/', views.Listar_Staff.as_view(), name='tabela_equipe'),
    path('tabela_equipe/<int:pk>/editar', views.Atualizar_membro_Equipe.as_view(), name='atualizar_equipe'),
    path('cadastrar_equipe', views.CadastrarEquipe.as_view(), name='cadastrar_equipe'),
    path('tabela_equipe/<int:pk>/deletar', views.DeleteEquipe.as_view(), name='deletar_equipe'),


    #cliente
    path('tabela_cliente/', views.Listar_Clientes.as_view(), name='tabela_cliente'),
    path('cadastrar_cliente', views.Cadastrar_Cliente.as_view(), name='cadastrar_cliente'),
    path('tabela_cliente/<int:pk>/editar', views.Atualizar_Cliente.as_view(), name='atualizar_cliente'),
    path('tabela_cliente/<int:pk>/deletar', views.DeleteCliente.as_view(), name='deletar_cliente'),






    #vendas

    path('tabela_venda/', views.Listar_Vendas.as_view(), name='tabela_venda'),
    path('cadastrar_venda/<int:pk>', views.Cadastrar_Vendas.as_view(), name='cadastrar_venda'),








    #atualização




    #deletar



    #visualizar registros individuais

]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

