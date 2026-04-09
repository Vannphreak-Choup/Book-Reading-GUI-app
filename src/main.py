import os
import sys
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk
from Functionality_UI_Data import UI, functionality
from Functionality_UI_Data.functionality import _register_file

# store the library folder in a variable so it can be used across different os
LIBARY_DIR = Path.home() / "ReadDaBookLibrary"
# create a dir on the first run and does nothing
LIBARY_DIR.mkdir(parents=True, exist_ok=True)

# give functionality.py the resolved path so _copy_to_library know where to save files
functionality.LIBARY_DIR = LIBARY_DIR

# the app set up color
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# the app icon or logo
def set_app_icon(app):
    try:
        # check for window os
        if sys.platform == "win32":
            ico_path = "src/assets/title_icon/book2.ico"
            if not os.path.exists(ico_path):
                img = Image.open("src/assets/title_icon/book2.png")
                img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (64, 64)])
            app.iconbitmap(ico_path)
        # check for mac os
        elif sys.platform == "darwin":
            img = Image.open("src/assets/title_icon/book2.png").resize((64, 64))
            photo = ImageTk.PhotoImage(img)
            app.iconphoto(True, photo)
            app._icon_photo = photo
        else:
            # check for linux os
            img = Image.open("src/assets/title_icon/book2.png").resize((32, 32))
            photo = ImageTk.PhotoImage(img)
            app.iconphoto(True, photo)
            app._icon_photo = photo
    except Exception as e:
        print(f"Could not set icon: {e}")

# create a window to open
app = ctk.CTk()
set_app_icon(app)
# the app title
app.title("Read da book")
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
