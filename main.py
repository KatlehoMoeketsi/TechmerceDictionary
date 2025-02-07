'''
This project will serve as a dictionary app that uses tkinter in v1.0, then kivy in the next iteration. v2.0
 We will be using the Free Dictionary API as the source and then develop the offline mode in the v2.1
 Lets get coding
'''

#Step 1: Make an HTTP request to the API
#Step 2: Parse the JSON response
#Step 3: Display the extracted information
#Step 4: Modify the GUI


import requests
import tkinter as tk
from tkinter import messagebox

def get_definition():
    word = entry.get()
    if not word:
        messagebox.showerror("Error", "Please enter a word")
        return

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(url)
        data = response.json()

        if isinstance(data, list):
            meaning = data[0]['meanings'][0]['definitions'][0]['definition']
            # print(meaning)
            result_label.config(text=f"Definition: {meaning}")
        else:
            result_label.config(text="Word not found")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch definition: {e}")



root = tk.Tk()
root.title('TechmerceDictionary')


#UI elements
tk.Label(root, text="Enter a Word:"). pack(pady=5)
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Button(root, text="Search", command=get_definition).pack(pady=5)
result_label = tk.Label(root, text="", wraplength=400, justify="left")
result_label.pack(pady=10)

root.mainloop()


