from shlex import quote

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner


from historylist import HistoryList
from kivy.uix.popup import Popup
import requests
import sqlite3




class DictionaryApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quote_label = None
        self.history_list = None
        self.conn = sqlite3.connect('word_history.db')
        self.create_table()
        self.result_label = None
        self.search_button = None
        self.word_input = None
        self.layout = None
        self.history_spinner = None

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=5, spacing=10)
        print("History of words:", self.get_word_history())

        #Quote code
        #
        quotebuild = get_inspirational_quote()
        self.quote_label = Label(text=quotebuild, size=(1, 0.2), halign="center", valign="middle")
        self.quote_label.bind(size=self.quote_label.setter('text_size'))
        self.layout.add_widget(self.quote_label)

        self.word_input = TextInput(hint_text="Enter a word", size_hint=(1, 0.1), halign="center")
        self.layout.add_widget(self.word_input)


        #Button build
        self.search_button = Button(text="Search", size_hint=(1, 0.1), font_size=20)
        self.search_button.bind(on_press=self.fetch_definition)
        self.layout.add_widget(self.search_button)

        #word History List
        self.history_list = HistoryList(self, size_hint=(1,0.4))
        self.layout.add_widget(self.history_list)

        #Label Build
        self.result_label = Label(text="", size_hint=(1, 0.3), halign="left", valign="top")
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        #Load word history on startup
        self.history_list.update_history(self.get_word_history())

        return self.layout

    #Fetching dictionary term from API
    def fetch_definition(self, instance):
        word = self.word_input.text.strip()
        if not word:
            msg = ""
            self.show_popup(msg)
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
                self.add_word_history(word)
            else:
                self.result_label.text = f"{word} Not Found"

        except requests.exceptions.RequestException as e:
            self.result_label.text = f"Error: {e}"
    #SQL table creation
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE
                )
            ''')
        self.conn.commit()
    #Word History Management
    #1. Gets the word history from the database
    def get_word_history(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT word FROM history ORDER BY id DESC LIMIT 100')

        return [row[0] for row in cursor.fetchall()]

    #2. Add words from the logic
    def add_word_history(self, word):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO history (word) VALUES (?)', (word,))
        self.conn.commit()
        #Update UI
        self.history_list.update_history(self.get_word_history())

    #3. Selects the word from the Spinner Widget
    def select_word(self, word):
        self.word_input.text = word
        self.fetch_definition(None)

    @staticmethod
    def show_popup(instance):
        content = BoxLayout(orientation="vertical", size_hint_y=None)
        label = Label(text="Please enter text, and try again", text_size=(None, None), size_hint_x=1, halign='center')
        label.bind(texture_size=label.setter('size'))
        close_button = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(label)
        content.add_widget(close_button)

        popup = Popup(title="Error", content=content,auto_dismiss=False)

        close_button.bind(on_press=popup.dismiss)
        content.bind(minimum_size=content.setter('size'))
        popup.open()

def get_inspirational_quote():
   try:
       response = requests.get('https://zenquotes.io/api/random')
       data = response.json()
       if isinstance(data,list) and len(data) > 0:
           varquote = data[0]['q']
           author = data[0]['a']
           return f"{varquote} - {author}"
       else:
           return "No quote available."
   except requests.exceptions.RequestException as e:
       return f"Error fetching quote: {e}"
