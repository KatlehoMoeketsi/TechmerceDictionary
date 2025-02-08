from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import requests
import sqlite3

class DictionaryApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect('word_history.db')
        self.create_table()
        self.result_label = None
        self.search_button = None
        self.word_input = None
        self.layout = None

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.word_input = TextInput(hint_text="Enter a word", size_hint=(1, 0.1), halign="center")
        self.layout.add_widget(self.word_input)

        self.search_button = Button(text="Search", size_hint=(1, 0.1), font_size=20)
        self.search_button.bind(on_press=self.fetch_definition)
        self.layout.add_widget(self.search_button)

        self.result_label = Label(text="", size_hint=(1, 0.8), halign="left", valign="top", font_size=20)
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        return self.layout

    def fetch_definition(self, instance):
        word = self.word_input.text.strip()
        if not word:
            self.result_label.text = "Please enter a word"
            return

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

        try:
            response = requests.get(url)
            data = response.json()

            if isinstance(data, list):
                meaning = data[0]['meanings'][0]['definitions'][0]['definition']
                part_of_speech = data[0]['meanings'][0]['partOfSpeech']
                print(data[0]['meanings'][0]['partOfSpeech'])
                self.result_label.text=f"({part_of_speech}) Definition: {meaning}"
            else:
                self.result_label.text = f"{word} Not Found"

        except requests.exceptions.RequestException as e:
            self.result_label.text = f"Error: {e}"

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE
                )
            ''')
        self.conn.commit()

