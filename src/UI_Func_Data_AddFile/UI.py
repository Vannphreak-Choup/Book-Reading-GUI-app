import customtkinter as ctk
from PIL import Image
from UI_Func_Data_AddFile import Data
from UI_Func_Data_AddFile.functionality import handle_add_pdf, open_pdf, remove_pdf, zoom_in, zoom_out, poll_scroll, set_canvas

def build(app):
    Data.app = app
    # the font we use for all buttons and Labels in the UI
    my_font = ctk.CTkFont(family="Arial", size=15, weight="bold")

    # the top frame
    top_frame = ctk.CTkFrame(app)
    top_frame.pack(fill="x", padx=10, pady=5)
    # helper function to add icons to the buttons
    def make_icon(path):
        img = Image.open(path)
        return ctk.CTkImage(
            light_image=img, 
            dark_image=img, 
            size=(20, 20)
        )
    
    # add pdf button
    btn_add = ctk.CTkButton(
        top_frame, 
        text="Add PDF",
        image=make_icon("assets/icon/add.png"),
        compound="left", 
        command=handle_add_pdf, 
        font=my_font
    )
    btn_add.pack(side="left", padx=5)
    
    # open button
    btn_open = ctk.CTkButton(
        top_frame, 
        text="Open",
        image=make_icon("assets/icon/open.png"),
        compound="left", 
        command=open_pdf, 
        font=my_font
    )
    btn_open.pack(side="left", padx=5)
    
    # remove button
    btn_remove = ctk.CTkButton(
        top_frame, 
        text="Remove",
        image=make_icon("assets/icon/remove.png"),
        compound="left", 
        command=remove_pdf, 
        font=my_font
    )
    btn_remove.pack(side="left", padx=5)
    
    # zoom in button
    btn_zoom_in = ctk.CTkButton(
        top_frame, 
        text="Zoom",
        image=make_icon("assets/icon/zoom_in.png"),
        compound="left", 
        command=zoom_in, 
        font=my_font
    )
    btn_zoom_in.pack(side="right", padx=5)
    
    # zoom out button
    btn_zoom_out = ctk.CTkButton(
        top_frame, 
        text="Zoom",
        image=make_icon("assets/icon/zoom_out.png"),
        compound="left", 
        command=zoom_out, 
        font=my_font
    )
    btn_zoom_out.pack(side="right", padx=5)

    # content frame
    content_frame = ctk.CTkFrame(app)
    content_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # left frame
    left_frame = ctk.CTkFrame(
        content_frame, 
        border_color="gray50", 
        border_width=3
    )
    left_frame.pack(side="left", fill="y", padx=5)

    ctk.CTkLabel(
        left_frame, 
        text="My Files", 
        font=my_font
    ).pack(anchor="w", padx=5, pady=2.5)

    Data.file_list = ctk.CTkScrollableFrame(left_frame)
    Data.file_list.pack(fill="both", expand=True)

    # right frame
    right_frame = ctk.CTkFrame(content_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=5)

    scrollbar = ctk.CTkScrollbar(right_frame)
    scrollbar.pack(side="right", fill="y")

    # background colour matches CTk dark/light mode reasonably well
    canvas = ctk.CTkCanvas(
        right_frame,
        bg="#2b2b2b",
        highlightthickness=0,
        yscrollcommand=scrollbar.set
    )
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.configure(command=canvas.yview)

    # mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # Windows and MacOS
    canvas.bind("<MouseWheel>", _on_mousewheel)
    # Linux
    canvas.bind("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units")) 
    canvas.bind("<Button-5>",   lambda e: canvas.yview_scroll( 1, "units")) 

    # hand the canvas to functionality.py
    set_canvas(canvas)

    # start the scroll polling loop
    Data.app.after(100, poll_scroll)