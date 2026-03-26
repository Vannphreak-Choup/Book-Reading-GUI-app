import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("Dark")   # dark mode
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Read da book")
app_icon = "assets/icon/book2.ico"
app.iconbitmap(app_icon)
app.geometry("900x500")

# the 3 buttons frame on top
top_frame = ctk.CTkFrame(app)
top_frame.pack(fill="x", padx=10, pady=5)

# Add pdf 
addImage = "assets/icon/add.png"        
AddPDF = Image.open(addImage)           
Add_icon = ctk.CTkImage(
    light_image=AddPDF, 
    dark_image=AddPDF, 
    size=(20, 20)
)

btn_add = ctk.CTkButton(
    top_frame, 
    text="Add PDF", 
    image=Add_icon, 
    compound="left"

)
btn_add.pack(side="left", padx=5)

# Open
openImage = "assets/icon/open.png"      
Open = Image.open(openImage)
Open_icon = ctk.CTkImage(
    light_image=Open,
    dark_image=Open,
    size=(20, 20)
)

btn_open = ctk.CTkButton(
    top_frame, 
    text="Open",
    image=Open_icon,
    compound="left"
)
btn_open.pack(side="left", padx=5)

# Remove
removeImage = "assets/icon/remove.png"
remove = Image.open(removeImage)
remove_icon = ctk.CTkImage(
    light_image=remove,
    dark_image=remove,
    size=(20, 20)
)

btn_remove = ctk.CTkButton(
    top_frame,
    text="Remove",
    image=remove_icon,
    compound="left"
)
btn_remove.pack(side="left", padx=5)

# frame for both the left and right 
content_frame = ctk.CTkFrame(app)
content_frame.pack(fill="both", expand=True, padx=10, pady=5)

# left frame 
left_frame = ctk.CTkFrame(content_frame, width=200)
left_frame.pack(side="left", fill="y", padx=5, pady=5)

# file list in the left frame
file_list = ctk.CTkScrollableFrame(left_frame)
file_list.pack(fill="both", expand=True)

# right frame
right_frame = ctk.CTkFrame(content_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

# the viewer content in the right frame
viewer = ctk.CTkLabel(right_frame, text="PDF")
viewer.pack(fill="both", expand=True)


# open the app
app.mainloop()