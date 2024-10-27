import customtkinter as ctk
import json
from src import ui, visualisation, finance

ctk.set_appearance_mode("System")  # System (default), Dark, Light
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = ui.App()
app.mainloop()