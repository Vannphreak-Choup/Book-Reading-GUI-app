import customtkinter as ctk
import fitz
from PIL import Image, ImageTk
from button import add_pdf
import data


# the app set up color
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# create a window to open 
app = ctk.CTk()
# the app title
app.title("Read da book")
# the app icon or logo
app_icon = "assets/icon/book2.ico"
app.iconbitmap(app_icon)
# the size of the app in app when not open fullscreen
app.geometry("900x500")
# to store pdf images
pdf_images = []
# the font and size we use for the app
my_font = ctk.CTkFont(family="Arial", size=15, weight="bold")

# function to handle the add pdf button click
def handle_add_pdf():
    # return the file path and name as file path and file name
    filepath, filename = add_pdf()
    # if a file is selected, add the file name to the file list
    if filepath:
        data.pdf_files[filename] = filepath

        Label = ctk.CTkLabel(file_list, text=filename)
        Label.pack(anchor="w", padx=5)

        # listen for left mouse click
        Label.bind("<Button-1>", lambda e, name=filename: select_file(name))

# when user click a file it save which file is selected and print it out
def select_file(filename):
    data.selected_files = filename
    print(f"selected: {filename}")

# when user click open it checks if there is a file to select
def open_pdf():
    global pdf_images
    if not data.selected_files:
        print("No file selected")
        return

    # if there is it look inside the data and display the filepath
    filepath = data.pdf_files[data.selected_files]
    
    # loop inside the pdf containter and get everything inside it using .winfo_children()
    for widget in pdf_containter.winfo_children():
        # clear the screen so the new pdf don't stack on top of the old one
        widget.destroy()
    # clear the pdf image list so it doesn't store the old one when you open a new one
    pdf_images.clear()

    try:
        doc = fitz.open(filepath)
        # loop through all the page
        for page_num in range(len(doc)):
            # load the page one at a time
            page = doc.load_page(page_num)
            # render the page into pixel like a screenshot
            pix = page.get_pixmap()

            # convert those pixel into image using PIL (pillow)
            # (RGB for color), (pix.width and pix.height for image size), (pix.samples for pixel data)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # resize the image to fit the UI
            img = img.resize((2000, int(2000 * pix.height / pix.width)))

            # convert it into what tkinter can display and add it into the pdf images
            tk_img = ImageTk.PhotoImage(img)
            pdf_images.append(tk_img)

            # create a label widget and display the image (for the (text=""), this one remove the text)
            label = ctk.CTkLabel(pdf_containter, image=tk_img, text="")
            label.pack(anchor="center", pady=10)
    except Exception as e:
        print(f"Error Printing PDF: {e}")

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
    compound="left",
    command=handle_add_pdf,
    font=my_font

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
    compound="left", 
    command=open_pdf,
    font=my_font
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
    compound="left", 
    font=my_font
)
btn_remove.pack(side="left", padx=5)

# frame for both the left and right 
content_frame = ctk.CTkFrame(app)
content_frame.pack(fill="both", expand=True, padx=10, pady=5)

# left frame 
left_frame = ctk.CTkFrame(content_frame, border_color="gray50", border_width=3)
left_frame.pack(side="left", fill="y", padx=5)

# the top left frame below the buttons
leftFrameDesign = ctk.CTkLabel(left_frame, text="My Files", font=my_font)
leftFrameDesign.pack(anchor="w", padx=5, pady=2.5)

# file list in the left frame
file_list = ctk.CTkScrollableFrame(left_frame)
file_list.pack(fill="both", expand=True)

# right frame
right_frame = ctk.CTkFrame(content_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=5)

# the pdf container on the right frame
pdf_containter = ctk.CTkScrollableFrame(right_frame)
pdf_containter.pack(fill="both", expand=True)


# open the app
app.mainloop()