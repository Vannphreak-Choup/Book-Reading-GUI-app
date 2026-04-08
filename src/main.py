import os
from pathlib import Path
import customtkinter as ctk
from Functionality_UI_Data import UI, functionality
from Functionality_UI_Data.functionality import _register_file

# store the library folder in a variable so it can be used across different os
LIBARY_DIR = Path.home() / "ReadDaBookLibrary"
# create a dir on the first run and does nothing
Path.mkdir(LIBARY_DIR, exist_ok=True)

# give functionality.py the resolved path so _copy_to_library know where to save files
functionality.LIBARY_DIR = LIBARY_DIR

# the app set up color
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# create a window to open
app = ctk.CTk()
# the app title
app.title("Read da book")
# the app icon or logo
app.iconbitmap("assets/icon/book2.ico")
# the size of the app when not open fullscreen
app.geometry("1200x600")

# build the UI and attach it to the app window
UI.build(app)

'''restore previously added files from the library folder on startup'''
# lists every file in the library folder. sorted() puts them in alphabetical order so the list always appears in the same order regardless of filesystem ordering.
for fname in sorted(os.listdir(LIBARY_DIR)):
    if fname.lower().endswith(".pdf"):
        fpath = os.path.join(LIBARY_DIR, fname)
        _register_file(fpath, fname)

# open the app (i could've used the just app.mainloop() but if i added __name__ == "__main__" it looks cooler lol)
if __name__ == "__main__":
    app.mainloop()
