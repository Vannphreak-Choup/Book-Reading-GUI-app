import threading
import fitz
from PIL import Image
import customtkinter as ctk
from UI_Func_Data_AddFile.AddFile import add_pdf
from UI_Func_Data_AddFile import Data

# the default zoom level when opening a pdf file
zoom_level = 1.0

# a variable to track the generation of the render, we use it to cancel the render when the user opens a new pdf or zooms
render_generation = 0

# used to debounce zoom so rapid clicks don't spawn many threads
_zoom_after_id = None

# used to debounce the scroll check so it doesn't fire on every pixel
_scroll_after_id = None

# initialize the current page to 0 when opening a pdf file
current_page = 0

# how many pages above and below the visible area we render ahead of time
BUFFER_PAGES = 15

# function to handle the add pdf button click
def handle_add_pdf():
    # return the file path and name as filepath and filename
    filepath, filename = add_pdf()
    # if a file is selected, add the file name to the file list
    if filepath:
        Data.pdf_files[filename] = filepath

        Label = ctk.CTkLabel(Data.file_list, text=filename)
        Label.pack(anchor="w", padx=5)
        # store the filename as key and the label as value inside file_labels
        Data.file_labels[filename] = Label

        # listen for left mouse click
        Label.bind("<Button-1>", lambda e, name=filename: select_file(name))

# when user clicks a file it saves which file is selected and prints it out
def select_file(filename):
    Data.selected_files = filename

    # check inside the file_labels value and highlight the selected file as gray when the user clicks on the file
    for lbl in Data.file_labels.values():
        lbl.configure(fg_color="transparent")
    Data.file_labels[filename].configure(fg_color="gray")

    print(f"selected file: {filename}")

# when user clicks zoom in it increases the zoom level by 0.2
# debounced so rapid clicks only trigger one render
def zoom_in():
    global zoom_level, _zoom_after_id
    zoom_level += 0.2
    if _zoom_after_id:
        Data.app.after_cancel(_zoom_after_id)
    _zoom_after_id = Data.app.after(300, setup_placeholders)

# when user clicks zoom out it decreases the zoom level by 0.2, but it will not go below 0.4
def zoom_out():
    global zoom_level, _zoom_after_id
    zoom_level = max(0.4, zoom_level - 0.2)
    if _zoom_after_id:
        Data.app.after_cancel(_zoom_after_id)
    _zoom_after_id = Data.app.after(300, setup_placeholders)

# when user clicks open it checks if there is a file selected
def open_pdf():
    global current_page
    if not Data.selected_files:
        print("No file selected")
        return

    # if there is, look inside the Data and get the filepath
    filepath = Data.pdf_files[Data.selected_files]

    # open the file path using fitz
    Data.doc = fitz.open(filepath)

    # set up the placeholder frames and start lazy loading
    setup_placeholders()

# when user clicks remove it checks if there is a file selected
def remove_pdf():
    if not Data.selected_files:
        print("No file selected")
        return
    # if so:
    # remove the file from the Data
    del Data.pdf_files[Data.selected_files]
    # remove the label from the file list
    Data.file_labels[Data.selected_files].destroy()
    # remove the label from the Data
    del Data.file_labels[Data.selected_files]
    # clear the selected file
    Data.selected_files = None

    # clear the pdf container
    for widget in Data.pdf_container.winfo_children():
        widget.destroy()

    # clear all stored page Data
    Data.pdf_images.clear()
    Data.page_frames.clear()
    Data.page_rendered.clear()

# calculate the width and height of a page at the current zoom level without fully rendering it
# we use this to set the placeholder frame size so the scrollbar feels accurate
def get_page_size(page_num):
    page = Data.doc.load_page(page_num)
    rect = page.rect
    width = int(rect.width * zoom_level)
    height = int(rect.height * zoom_level)
    return width, height

# create one empty gray frame per page so the scrollbar knows the full document height
# we only fill in the actual image when the page scrolls into view
def setup_placeholders():
    global render_generation
    render_generation += 1

    # clear everything first
    for widget in Data.pdf_container.winfo_children():
        widget.destroy()
    Data.pdf_images.clear()
    Data.page_frames.clear()
    Data.page_rendered.clear()

    if Data.doc is None:
        return

    # create a gray placeholder frame for every page in the document
    for page_num in range(len(Data.doc)):
        width, height = get_page_size(page_num)

        # the outer frame acts as the placeholder with a fixed size
        frame = ctk.CTkFrame(
            Data.pdf_container, 
            width=width, 
            height=height, 
            fg_color="gray20"
        )
        frame.pack(pady=10)
        frame.pack_propagate(False)

        # store the frame so we can fill it in later when it becomes visible
        Data.page_frames[page_num] = frame
        # track whether this page has been rendered yet
        Data.page_rendered[page_num] = False

    # listen for scroll events so we know when to render new pages
    Data.pdf_container._parent_canvas.bind("<Configure>", lambda e: on_scroll())
    Data.pdf_container._parent_canvas.bind("<MouseWheel>", lambda e: on_scroll())
    Data.pdf_container._parent_canvas.bind("<Button-4>", lambda e: on_scroll())
    Data.pdf_container._parent_canvas.bind("<Button-5>", lambda e: on_scroll())

    # make the inner canvas stretch to fill the full width of the scrollable frame
    # so pages stay centered even when the window is resized or goes fullscreen
    Data.pdf_container._parent_canvas.bind("<Configure>", lambda e: (
    Data.pdf_container._parent_canvas.itemconfig("all", width=e.width),
    on_scroll()
))

    # do the first render pass right away for the pages already in view
    on_scroll()

# called whenever the user scrolls, checks which pages are now visible and renders them
def on_scroll():
    global _scroll_after_id
    # debounce so we don't check on every single scroll pixel
    if _scroll_after_id:
        Data.app.after_cancel(_scroll_after_id)
    _scroll_after_id = Data.app.after(100, check_visible_pages)

# figure out which pages are currently visible inside the scrollable frame
# figure out which pages are currently visible inside the scrollable frame
def check_visible_pages():
    if Data.doc is None or not Data.page_frames:
        return

    # get the canvas inside the scrollable frame
    canvas = Data.pdf_container._parent_canvas

    # get the visible scroll range as fractions (0.0 to 1.0)
    scroll_top_frac, scroll_bottom_frac = canvas.yview()

    # get the total scrollable height of the canvas content
    canvas.update_idletasks()
    total_height = canvas.winfo_height()
    scroll_region = canvas.cget("scrollregion")

    # if there is a scroll region set, use its height instead
    if scroll_region:
        try:
            total_height = float(scroll_region.split()[3])
        except Exception:
            total_height = canvas.winfo_height()

    # convert fractions to actual pixel positions
    visible_top = scroll_top_frac * total_height
    visible_bottom = scroll_bottom_frac * total_height

    # if the pdf is short enough to fit without scrolling, just render everything
    if scroll_top_frac == 0.0 and scroll_bottom_frac == 1.0:
        for page_num in Data.page_frames:
            if not Data.page_rendered[page_num]:
                Data.page_rendered[page_num] = True
                threading.Thread(
                    target=render_page_thread,
                    args=(page_num, render_generation),
                    daemon=True
                ).start()
        return

    # check every page frame to see if it overlaps with the visible area
    for page_num, frame in Data.page_frames.items():
        # skip if already rendered
        if Data.page_rendered[page_num]:
            continue

        # get the frame's position inside the scrollable canvas
        try:
            frame.update_idletasks()
            frame_top = frame.winfo_y()
            frame_bottom = frame_top + frame.winfo_height()
        except Exception:
            continue

        # add a buffer so we render pages slightly before they scroll into view
        buffer = frame.winfo_height() * BUFFER_PAGES

        # if the frame overlaps with the visible area (plus buffer), render it
        if frame_bottom + buffer >= visible_top and frame_top - buffer <= visible_bottom:
            Data.page_rendered[page_num] = True
            threading.Thread(
                target=render_page_thread,
                args=(page_num, render_generation),
                daemon=True
            ).start()

# render a single page in the background thread and then display it on the main thread
def render_page_thread(page_num, my_generation):
    if Data.doc is None:
        return

    try:
        # if the generation changed it means the user opened a new file or zoomed, so cancel
        if my_generation != render_generation:
            return

        page = Data.doc.load_page(page_num)
        # we use the zoom level to render the page, so when the user zooms it will render with the new zoom level
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_level, zoom_level))
        # convert the pixmap to image using PIL
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        # free the raw pixmap bytes immediately to save memory
        del pix

        # if the generation is still the same, display the page on the main thread
        if my_generation == render_generation:
            Data.app.after(0, lambda img=img, num=page_num, gen=my_generation: display_page(img, num, gen))
    except Exception as e:
        print(f"Thread error on page {page_num}: {e}")

# display a single rendered page inside its placeholder frame
def display_page(img, page_num, my_generation):
    # if the generation changed, don't display anything
    if my_generation != render_generation:
        return

    # check the frame still exists
    if page_num not in Data.page_frames:
        return

    ctk_img = ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=(img.width, img.height)
    )
    # store the image so it doesn't get garbage collected
    Data.pdf_images.append(ctk_img)

    # put the image label inside the placeholder frame
    frame = Data.page_frames[page_num]
    label = ctk.CTkLabel(
        frame,
        image=ctk_img,
        text="",
        compound="top"
    )
    label.pack()