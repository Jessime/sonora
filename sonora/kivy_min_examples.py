from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from sonora.buttons import GotoLoginScreenBtn, GotoCreateAccountBtn, BackStartScreenBtn

from pprint import pprint


class UsernamePassword(GridLayout):

    def __init__(self, **kwargs):
        super(UsernamePassword, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='Username:'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='Password:'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)


class LoginSpace(BoxLayout):

    def __init__(self, **kwargs):
        super(LoginSpace, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.login_input_space = UsernamePassword()
        self.add_widget(self.login_input_space)
        self.add_widget(Button(text="Login"))


class CreateAccountSpace(BoxLayout):

    def __init__(self, **kwargs):
        super(CreateAccountSpace, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.create_account_input_space = UsernamePassword()
        self.add_widget(self.create_account_input_space)
        self.add_widget(Button(text="Create Account"))


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.login_space = LoginSpace(size_hint=(1, .2))
        self.layout.add_widget(self.login_space)
        self.layout.add_widget(BackStartScreenBtn())
        blank_space = BoxLayout(size_hint=(1, .7))
        self.layout.add_widget(blank_space)


class CreateAccountScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateAccountScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.create_account_space = CreateAccountSpace(size_hint=(1, .2))
        self.layout.add_widget(self.create_account_space)
        self.layout.add_widget(BackStartScreenBtn())
        blank_space = BoxLayout(size_hint=(1, .7))
        self.layout.add_widget(blank_space)


class StartScreen(Screen):

    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=2)
        self.add_widget(self.layout)
        self.create_btn = self.layout.add_widget(GotoCreateAccountBtn())
        self.login_btn = self.layout.add_widget(GotoLoginScreenBtn())


class SonoraApp(App):

    def build(self):
        # Create the screen manager
        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen(name='start'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(CreateAccountScreen(name='create_account'))
        return self.sm

