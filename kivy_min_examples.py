from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from pprint import pprint
# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        Button:
            text: 'Goto settings'
            on_press: root.manager.current = 'settings'
        Button:
            text: 'Quit'

<SettingsScreen>:
    BoxLayout:
        Button:
            text: 'My settings button'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
""")

def callback(instance):
    print('The button <%s> is being pressed' % instance.text)
    instance.parent.parent.parent.current = "login"

# Declare both screens
class StartScreen(Screen):

    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=2)
        self.add_widget(self.layout)
        self.create_btn = self.layout.add_widget(Button(text="Create Account"))
        self.login_btn = self.layout.add_widget(Button(text="Login", on_press=callback))
        print("got here")


class BackToStartBtn(Button):

    def __init__(self, **kwargs):
        super(BackToStartBtn, self).__init__(**kwargs)

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
        self.layout.add_widget(Button(text="Back", size_hint=(1, .1)))
        blank_space = BoxLayout(size_hint=(1, .7))
        self.layout.add_widget(blank_space)


class CreateAccountScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateAccountScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.create_account_space = CreateAccountSpace(size_hint=(1, .2))
        self.layout.add_widget(self.create_account_space)
        self.layout.add_widget(Button(text="Back", size_hint=(1, .1)))
        blank_space = BoxLayout(size_hint=(1, .7))
        self.layout.add_widget(blank_space)


class SonoraApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(LoginScreen(name='login'))

        return sm

if __name__ == '__main__':
    SonoraApp().run()
