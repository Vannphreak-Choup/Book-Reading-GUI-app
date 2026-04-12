import os
import sys
import json
from importlib.resources import files
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk
from .utils import UI, functionality, Data
from .utils.functionality import _register_file

# store the library folder in a variable so it can be used across different os
LIBARY_DIR = Path.home() / "ReadDaBookLibrary"
# create a dir on the first run and does nothing
LIBARY_DIR.mkdir(parents=True, exist_ok=True)
# store the progress file in a variable so it can be used across different os
PROGRESS_FILE = LIBARY_DIR / "progress.json"

# the app icon or logo
def set_app_icon(app):
    try:
        # windows OS
        if sys.platform == "win32":
            ico_path = LIBARY_DIR / "book2.ico"
            if not ico_path.exists():
                src = files("pdfreading.assets.title_icon").joinpath("book2.png")
                img = Image.open(src)
                img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (64, 64)])
            app.iconbitmap(str(ico_path))
        # macOS
        elif sys.platform == "darwin":
            src = files("pdfreading.assets.title_icon").joinpath("book2.png")
            img = Image.open(src).resize((64, 64))
            photo = ImageTk.PhotoImage(img)
            app.iconphoto(True, photo)
            app._icon_photo = photo
        else:
            # linux and other OSes
            src = files("pdfreading.assets.title_icon").joinpath("book2.png")
            img = Image.open(src).resize((32, 32))
            photo = ImageTk.PhotoImage(img)
            app.iconphoto(True, photo)
            app._icon_photo = photo
    except Exception as e:
        print(f"Could not set icon: {e}")

# load the user's reading progress
def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r") as f:
                # load the last read pages from the progress file.
                Data.last_read_pages.update(json.load(f))
        except Exception:
            # if there's an error loading the progress (e.g. file is corrupted), just ignore it and start with an empty progress.
            pass

# save the user's reading progress to a file so it can be loaded on the next startup
def save_progress():
    # if there's a currently selected file and an open document, save the current page to the last_read_pages dict
    if Data.selected_file and Data.doc:
        Data.last_read_pages[Data.selected_file] = functionality._current_page
    try:
        # open the progress file for writing and save the last_read_pages dict as json. this way we can restore the user's last read page for each book on the next startup.
        with open(PROGRESS_FILE, "w") as f:
            json.dump(Data.last_read_pages, f)
    except Exception as e:
        print(f"Couldn't Save Progress: {e}")

def main():
    # give functionality.py the resolved path so _copy_to_library know where to save files
    functionality.LIBARY_DIR = LIBARY_DIR
    # the app set up color
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # create a window to open
    app = ctk.CTk()
    set_app_icon(app)
    # the app title
    app.title("Read da book")
    # the size of the app when not open fullscreen
    app.geometry("1200x600")

    # when the user closes the app, we want to save their progress before the app actually closes. this function is called by the WM_DELETE_WINDOW protocol handler below.
    def on_close():
        save_progress()
        app.destroy()

    # build the UI and attach it to the app window
    UI.build(app)
    load_progress()
    # set the on_close function to be called when the user tries to close the window, so we can save their progress first
    app.protocol("WM_DELETE_WINDOW", on_close)

    '''restore previously added files from the library folder on startup'''
    # lists every file in the library folder. sorted() puts them in alphabetical order so the list always appears in the same order regardless of filesystem ordering.
    for fname in sorted(os.listdir(LIBARY_DIR)):
        if fname.lower().endswith(".pdf"):
            fpath = os.path.join(LIBARY_DIR, fname)
            _register_file(fpath, fname)
    app.mainloop()

# open the app
if __name__ == "__main__":
    main()
