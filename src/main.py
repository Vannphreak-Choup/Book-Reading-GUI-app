import customtkinter as ctk
import threading
import fitz
from PIL import Image
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
# the size of the app when not open fullscreen
app.geometry("1200x600")


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
        # store the filename as key and the label as value inside file_labels
        data.file_labels[filename] = Label

        # listen for left mouse click
        Label.bind("<Button-1>", lambda e, name=filename: select_file(name))

# when user click a file it save which file is selected and print it out
def select_file(filename):
    data.selected_files = filename

    # check inside the file_labels value and highlight the selected file as gray when the user click on the file
    for lbl in data.file_labels.values():
        lbl.configure(fg_color="transparent")
    data.file_labels[filename].configure(fg_color="gray")
    
    print(f"selected file: {filename}")

# the default zoom level when open a pdf file
zoom_level = 1.0

# when user click this button it increase the zoom level by 0.2
def zoom_in():
    global zoom_level
    zoom_level += 0.2
    render_all_page()

# when user click this button it decrease the zoom level by 0.2, but it will not go beyond 0.4 because we don't want the page to be too small
def zoom_out():
    global zoom_level
    zoom_level = max(0.4, zoom_level - 0.2)
    render_all_page()

# initialize the current page to 0 when open a pdf file
current_page = 0

# when user click open it checks if there is a file to select
def open_pdf():
    global current_page
    if not data.selected_files:
        print("No file selected")
        return

    # if there is it look inside the data and display the filepath
    filepath = data.pdf_files[data.selected_files]
    
    # open the file path using fitz
    data.doc = fitz.open(filepath)

    render_all_page()

# when user click remove it check if there is a file to select
def remove_pdf():
    if not data.selected_files:
        print("No file selected")
        return
    # if so:
    # remove the file from the data
    del data.pdf_files[data.selected_files]
    # remove the label from the file list
    data.file_labels[data.selected_files].destroy()
    # remove the label from the data
    del data.file_labels[data.selected_files]
    # clear the selected file
    data.selected_files = None

    # clear the pdf container
    for widget in pdf_containter.winfo_children():
        widget.destroy()

# when user click zoom in/out it will call this function to render the page with the new zoom level
def render_all_page_thread(my_generation):
    # if the document is not open, return
    if data.doc is None:
        return

    try:
        for page_num in range(len(data.doc)):
            # if the generation is not the same as the current generation, it means the user has open a new pdf file or zoom in/out, so we cancel the render
            if my_generation != render_generation:
                print(f"Render {my_generation} cancelled")
                return
            # render the page
            page = data.doc.load_page(page_num)
            # we use the zoom level to render the page, so when the user zoom in/out it will render the page with the new zoom level
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom_level, zoom_level))
            # convert the pixmap to image using PIL
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # if the generation is the same as the current generation, it means the user has not open a new pdf file or zoom in/out, so we can display the page
            if my_generation == render_generation:
                app.after(0, lambda img=img, num=page_num, gen=my_generation: display_page(img, num, gen))
    except Exception as e:
        print(f"Thread error: {e}")

# display the page on the pdf container, and check the generation before displaying the page
def display_page(img, page_num, my_generation):
    if my_generation != render_generation:
        return
    
    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=(img.width, img.height)
    )
    data.pdf_images.append(ctk_img)
    label = ctk.CTkLabel(
        pdf_containter,
        image=ctk_img,
        text="",
        compound="top"
    )
    label.pack(pady=10)

# a variable to track the generation of the render, we will use it to cancel the render when the user open a new pdf file or zoom in/out
render_generation = 0

# render the current page of the pdf file
def render_all_page():
    global render_generation
    render_generation += 1
    my_generation = render_generation
    # clear old page immediately on the main thread before starting the thread
    for widget in pdf_containter.winfo_children():
        widget.destroy()
    data.pdf_images.clear()

    # start a new thread to render the page, so it will not block the main thread and the UI will still be responsive, 
    # we pass the current generation to the thread so it can check if the generation is still the same before displaying the page
    threading.Thread(
        target=render_all_page_thread,
        args=(my_generation,),
        daemon=True
    ).start()

'''All the line below are the main UI'''
# the 3 buttons frame on top
top_frame = ctk.CTkFrame(app)
top_frame.pack(fill="x", padx=10, pady=5)

# Add pdf button
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

# Open button
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

# Remove button
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
    command=remove_pdf, 
    font=my_font
)
btn_remove.pack(side="left", padx=5)

# Zoom in button
zoomin = "assets/icon/zoom_in.png"
zoomIN = Image.open(zoomin)
zoom_in_icon = ctk.CTkImage(
    light_image=zoomIN,
    dark_image=zoomIN,
    size=(20, 20)
)
btn_zoom_in = ctk.CTkButton(
    top_frame,
    text="Zoom",
    image=zoom_in_icon,
    compound="left",
    command=zoom_in,
    font=my_font
)
btn_zoom_in.pack(side="right", padx=5)

# Zoom out button
zoomout = "assets/icon/zoom_out.png"
zoomOUT = Image.open(zoomout)
zoom_out_icon = ctk.CTkImage(
    light_image=zoomOUT,
    dark_image=zoomOUT,
    size=(20, 20)
)
btn_zoom_out = ctk.CTkButton(
    top_frame,
    text="Zoom",
    image=zoom_out_icon,
    compound="left",
    command=zoom_out,
    font=my_font
)
btn_zoom_out.pack(side="right", padx=5)

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


# open the app (i could've used just app.mainloop() but if i added __name__ == "__main__" it looks cooler lol)
if __name__ == "__main__":
    app.mainloop()