from shlex import quote

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.theming import ThemeManager

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from historylist import HistoryList


import os

if os.name =='nt':
    db_dir = os.path.join(os.getenv('APPDATA'), "Dictionary")
else: #Linux & Mac OS
    db_dir = os.path.expanduser("~/dictionary")

if not os.path.exists(db_dir):
    # Ensure the directory exists
    os.makedirs(db_dir)

#Set the database file path
db_dir = os.path.join(db_dir, 'word_history.db')


import requests
import sqlite3




class DictionaryApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.dialog = None
        self.search_container = None
        self.history_heading = None
        self.quote_label = None
        self.history_list = None

        self.result_label = None
        self.search_button = None
        self.word_input = None
        self.layout = None
        self.history_spinner = None
        self.conn = sqlite3.connect(db_dir)
        self.create_table()

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=5, spacing=10)
        print("History of words:", self.get_word_history())

        #TOP SECTION - QUOTE
        quotebuild = get_inspirational_quote()
        self.quote_label = Label(text=quotebuild, size_hint_y=0.3, halign="center", valign="middle")
        self.quote_label.bind(size=self.quote_label.setter('text_size'))
        self.layout.add_widget(self.quote_label)


        #MIDDLE SECTION - MAIN
        self.search_container = BoxLayout(
            orientation="vertical",
            size_hint = (None,None),
            size=(300, 120),
            pos_hint={"center_x": 0.5}
        )
        #User Input build
        self.word_input = TextInput(hint_text="Enter a word", size_hint=(1, None),height=50,halign="center")
        #Button build
        self.search_button = Button(text="Search", size_hint=(1, None), height=50)
        self.search_button.bind(on_press=self.fetch_definition)

        #adding to MAIN SECTION
        self.search_container.add_widget(self.word_input)
        self.search_container.add_widget(self.search_button)
        self.layout.add_widget(self.search_container)


        #BOTTOM SECTION - HISTORY
        #word History List
        self.history_heading=Label(text="History", bold=True,size_hint_y=0.1,size_hint=(None,None), halign="left",font_size=16, height=20)
        self.history_list = HistoryList(self, size_hint_y=0.5)
        self.layout.add_widget(self.history_heading)
        self.layout.add_widget(self.history_list)

        #Label Build
        self.result_label = Label(text="", size_hint=(1, 0.3), halign="left", valign="top",padding=(20,))
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.layout.add_widget(self.result_label)

        #Load word history on startup
        self.history_list.update_history(self.get_word_history())
        return self.layout

    #Fetching dictionary term from API
    def fetch_definition(self, instance):
        word = self.word_input.text.strip().title()
        if not word:
            msg = "Please enter valid information"
            title = "Oops!"
            self.show_popup(title,msg)
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


    def show_popup(self, title,message):
        self.dialog = MDDialog(
            title=title,
            text = message,
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

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
