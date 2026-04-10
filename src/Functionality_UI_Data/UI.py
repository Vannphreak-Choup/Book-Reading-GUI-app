import customtkinter as ctk
from PIL import Image
from Functionality_UI_Data import Data
from Functionality_UI_Data.functionality import handle_add_pdf, open_pdf, remove_pdf, zoom_in, zoom_out, poll_scroll, set_canvas, prev_page, next_page, handle_add_url
from Functionality_UI_Data import functionality

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
        image=make_icon("src/assets/button_icon/add.png"),
        compound="left", 
        command=handle_add_pdf, 
        font=my_font,
        fg_color="#a51f1f",
        hover_color="#145a8a"
    )
    btn_add.pack(side="left", padx=5)

    btn_url = ctk.CTkButton(
        top_frame,
        text="From URL",
        image=make_icon("src/assets/button_icon/add.png"),
        compound="left",
        command=handle_add_url,
        font=my_font,
        fg_color="#a51f1f",
        hover_color="#145a8a"
    )
    btn_url.pack(side="left", padx=5)
    
    # open button
    btn_open = ctk.CTkButton(
        top_frame, 
        text="Open",
        image=make_icon("src/assets/button_icon/open.png"),
        compound="left", 
        command=open_pdf, 
        font=my_font,
        fg_color="#a51f1f",
        hover_color="#145a8a"
    )
    btn_open.pack(side="left", padx=5)
    
    # remove button
    btn_remove = ctk.CTkButton(
        top_frame, 
        text="Remove",
        image=make_icon("src/assets/button_icon/remove.png"),
        compound="left", 
        command=remove_pdf, 
        font=my_font,
        fg_color="#a51f1f",
        hover_color="#145a8a"
    )
    btn_remove.pack(side="left", padx=5)

    # zoom in button
    btn_zoom_in = ctk.CTkButton(
        top_frame, 
        text="Zoom",
        image=make_icon("src/assets/button_icon/zoom_in.png"),
        compound="left", 
        command=zoom_in, 
        font=my_font,
        fg_color="#55a51f",
        hover_color="#145a8a"
    )
    btn_zoom_in.pack(side="right", padx=5)
    
    # zoom out button
    btn_zoom_out = ctk.CTkButton(
        top_frame, 
        text="Zoom",
        image=make_icon("src/assets/button_icon/zoom_out.png"),
        compound="left", 
        command=zoom_out, 
        font=my_font,
            fg_color="#55a51f",
        hover_color="#145a8a"
    )
    btn_zoom_out.pack(side="right", padx=5)

    # separator gap between zoom and page nav
    ctk.CTkLabel(top_frame, text="", width=10).pack(side="right")

    # next page button  ▶
    btn_next = ctk.CTkButton(
        top_frame,
        text="▶",
        width=40,
        command=next_page,
        font=my_font,
        fg_color="#a57f1f",
        hover_color="#145a8a"
    )
    btn_next.pack(side="right", padx=2)

    # page input frame: [ entry ] / N
    page_nav_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
    page_nav_frame.pack(side="right", padx=4)

    # the editable page number entry
    Data.page_entry = ctk.CTkEntry(
        page_nav_frame,
        font=my_font,
        width=52,
        justify="center"
    )
    Data.page_entry.pack(side="left")
    Data.page_entry.bind("<Return>", lambda e: functionality.jump_to_entered_page())
    Data.page_entry.bind("<FocusOut>", lambda e: functionality.jump_to_entered_page())

    # the " / N" total pages label next to the entry
    Data.page_total_label = ctk.CTkLabel(
        page_nav_frame,
        text="/ --",
        font=my_font,
        anchor="w",
        width=50
    )
    Data.page_total_label.pack(side="left", padx=(4, 0))

    # prev page button  ◀
    btn_prev = ctk.CTkButton(
        top_frame,
        text="◀",
        width=40,
        command=prev_page,
        font=my_font,
        fg_color="#a57f1f",
        hover_color="#145a8a"
    )
    btn_prev.pack(side="right", padx=2)

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