from django.test import TestCase
from django.contrib.auth.models import User
from posvendasapp.forms import UsuarioForm
from posvendasapp.forms import EquipeForm
from posvendasapp.models import Equipe



# Create your tests here.

class UsuarioFormTest(TestCase):

    def setUp(self):
        User.objects.all().delete()

    def test_form_com_dados_validos(self):
        form_data = {
            'username': 'albert123',
            'email': 'albert@example.com',
            'password': 'Senha123',
            'password2': 'Senha123',
        }
        form = UsuarioForm(data=form_data)
        self.assertTrue(form.is_valid())
        User.objects.all().delete()

    def test_usuario_duplicado(self):
        User.objects.create_user(username='albert123', email='albert@teste.com', password='Senha123')

        form_data = {
            'username': 'albert123',
            'email': 'outroemail@example.com',
            'password': 'Senha123',
            'password2': 'Senha123',
        }
        # Form para criação (Usuario=None)
        form = UsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_edicao_usuario_mesmo_username(self):

        usuario = User.objects.create_user(username='albert123', email='albert@teste.com', password='Senha123')


        form_data = {
            'username': 'albert123',
            'email': 'albert@teste.com',
            'password': 'Senha123',
            'password2': 'Senha123',
        }
        form = UsuarioForm(Usuario=usuario, data=form_data)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_senha_curta(self):
        form_data = {
            'username': 'novo_user',
            'email': 'novo@example.com',
            'password': 'a1',
            'password2': 'a1',
        }
        form = UsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertIn('tamanho minimo', form.errors['password'][0].lower())

    def test_senha_sem_numero(self):
        form_data = {
            'username': 'usuario_alpha',
            'email': 'email@example.com',
            'password': 'SomenteLetras',
            'password2': 'SomenteLetras',
        }
        form = UsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertIn('letra e um número', form.errors['password'][0])

    def test_senhas_diferentes(self):
        form_data = {
            'username': 'usuario_diff',
            'email': 'diff@example.com',
            'password': 'Senha123',
            'password2': 'Senha456',
        }
        form = UsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertIn('password2', form.errors)



class EquipeFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='albert',
                                             email='albert@example.com',
                                             password='Senha123')

    def test_form_com_cargo_valido(self):
        form_data = {'Cargo': 'Gerente'}
        form = EquipeForm(data=form_data)
        self.assertTrue(form.is_valid())

        equipe = form.save(commit=False)
        equipe.Usuario = self.user
        equipe.save()

        self.assertEqual(equipe.Cargo, 'Gerente')
        self.assertEqual(equipe.Usuario.username, 'albert')

    def test_form_sem_cargo(self):
        form_data = {}  # sem enviar nada
        form = EquipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Cargo', form.errors)
        self.assertIn('obrigatório', form.errors['Cargo'][0].lower())

    def test_form_com_cargo_invalido(self):
        form_data = {'Cargo': 'CEO'}  # não está nos choices
        form = EquipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Cargo', form.errors)
        self.assertIn('Faça uma escolha válida', form.errors['Cargo'][0])
