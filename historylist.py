from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView


class HistoryList(RecycleView):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        self.layout = RecycleBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=5
        )

        self.layout.bind(minimum_height=self.layout.setter("height"))
        self.add_widget(self.layout)


        self.viewclass = "Button"
        self.data = []



    def update_history(self, words):
        """Update the history list."""
        self.data = [{"text": word,
                      "height":40,
                      "background_color":(0,0,0,0) ,
                      "color":(1,1,1,1),
                      "on_press": lambda btn=word: self.app.select_word(btn)} for word in words]
