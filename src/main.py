import customtkinter as ctk
from UI_Func_Data_AddFile import UI

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

# open the app (i could've used the just app.mainloop() but if i added __name__ == "__main__" it looks cooler lol)
if __name__ == "__main__":
    app.mainloop()
