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

# initialize the current page to 0 when opening a pdf file
current_page = 0

# track the last known scroll position to detect change
_last_scroll_pos = None

# how many pages above and below the visible area we render ahead of time
BUFFER_PAGES = 1

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
    # if there is already a zoom scheduled, cancel it and schedule a new one for 300ms later, 
    # so if the user clicks rapidly it won't spawn many renders but just wait until they are done zooming to render the pages
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

    # bind to the canvas configure event to check visible pages whenever the scroll region changes (e.g. when zooming)
    Data.pdf_container._parent_canvas.bind("<Configure>", lambda e: (
        Data.pdf_container._parent_canvas.itemconfig("all", width=e.width), 
        check_visible_pages()
))
    # start the scroll polling loop
    poll_scroll()

# when the user clicks open it calls this function to set up the placeholder frames and start lazy loading the pages as they scroll into view
def poll_scroll():
    global _last_scroll_pos
    # if there is an open document and there are page frames set up, check if the scroll position has changed since the last time we checked, 
    # and if so check which pages are visible and need to be rendered
    if Data.doc is not None and Data.page_frames:
        current_pos = Data.pdf_container._parent_canvas.yview()
        # if the scroll position has changed since the last time we checked, check which pages are visible and need to be rendered
        if current_pos != _last_scroll_pos:
            _last_scroll_pos = current_pos
            check_visible_pages()
    # check again after 100ms
    Data.app.after(100, poll_scroll)

# figure out which pages are currently visible inside the scrollable frame
def check_visible_pages():
    if Data.doc is None or not Data.page_frames:
        return
    # canvas = Data.pdf_container._parent_canvas gives us the canvas widget that is used for scrolling inside the CTkScrollableFrame, 
    # we need it to get the current scroll position and visible area
    canvas = Data.pdf_container._parent_canvas
    # we call update_idletasks to make sure the scroll region and widget positions are up to date 
    canvas.update_idletasks()

    # get the total scrollable content height from the scroll region
    scroll_region = canvas.cget("scrollregion")
    try:
        # if the scroll region is true we split it into 4 parts and take the 4th part which is the total height, otherwise we just use the canvas height as a fallback
        if scroll_region:
            total_height = float(scroll_region.split()[3])
        else:
            total_height = canvas.winfo_height()
    except Exception:
        total_height = canvas.winfo_height()

    # get visible range in pixels
    scroll_top_frac, scroll_bottom_frac = canvas.yview()
    visible_top = scroll_top_frac * total_height
    visible_bottom = scroll_bottom_frac * total_height

    # we loop through all the page frames
    for page_num, frame in Data.page_frames.items():
        # if this page has already been rendered, skip it
        if Data.page_rendered[page_num]:
            continue

        try:
            frame.update_idletasks()
            # winfo_rooty/rootx gives screen coords, so we convert to canvas content coords
            canvas_root_y = canvas.winfo_rooty()
            frame_screen_y = frame.winfo_rooty()
            # offset of the frame within the canvas content (accounts for scroll position)
            frame_top = frame_screen_y - canvas_root_y + visible_top
            frame_bottom = frame_top + frame.winfo_height()
        except Exception:
            continue
        
        # we add a buffer area above and below the visible area so pages just outside the view will also start rendering, 
        # this makes scrolling smoother because the page is more likely to be ready by the time the user scrolls to it
        buffer = frame.winfo_height() * BUFFER_PAGES

        # if any part of the frame is within the visible area plus buffer, 
        # we start rendering it in a background thread and mark it as rendered so we don't start multiple threads for the same page
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