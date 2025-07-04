from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Create your views here.



# Create your views here.


def posvendasteste(request):
    return HttpResponse('estou no posvendas')


def renderizarfechacliente(request):
    return render(request, 'posvendasapp/cliente_ficha.html')

class Login(LoginView):
    template_name = 'posvendasapp/tela_login.html'
    success_url = reverse_lazy('posvendasapp:menuinicial')
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.success_url


@login_required
def testelogin(request):
    return render(request, 'posvendasapp/menu_inicial.html')