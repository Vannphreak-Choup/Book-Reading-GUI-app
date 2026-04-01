import customtkinter as ctk
from PIL import Image
from UI_Func_Data_AddFile import Data
from UI_Func_Data_AddFile.functionality import handle_add_pdf, open_pdf, remove_pdf, zoom_in, zoom_out, poll_scroll

# build all the UI widgets and attach them to the app window
def build(app):
    # store the app reference so logic.py can call after() and after_cancel()
    Data.app = app

    # the font and size we use for the app
    my_font = ctk.CTkFont(family="Arial", size=15, weight="bold")

    '''All the lines below are the main UI'''
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

    # the top left frame label below the buttons
    leftFrameDesign = ctk.CTkLabel(left_frame, text="My Files", font=my_font)
    leftFrameDesign.pack(anchor="w", padx=5, pady=2.5)

    # file list in the left frame
    # store in Data so logic.py can add labels to it
    Data.file_list = ctk.CTkScrollableFrame(left_frame)
    Data.file_list.pack(fill="both", expand=True)

    # right frame
    right_frame = ctk.CTkFrame(content_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=5)

    # the pdf container on the right frame
    # store in Data so logic.py can render pages into it
    Data.pdf_container = ctk.CTkScrollableFrame(right_frame)
    Data.pdf_container.pack(fill="both", expand=True)

    # start the scroll polling loop that checks which pages are visible and need to be rendered, 
    # we call it here so when the app opens it will keep calling itself every 100ms to check for scroll changees and render pages as needed
    Data.app.after(100, poll_scroll)