import threading
import queue
import fitz
from PIL import Image, ImageTk
import customtkinter as ctk
from UI_Func_Data_AddFile.AddFile import add_pdf
from UI_Func_Data_AddFile import Data

# the default zoom level or initial value
zoom_level = 1.0
# every time a user open a new file or zoom this generation go up by one
# the worker thread compares its saved generation against this value, so if they are different outdated and thrown away without displaying
render_generation = 0

# store the id returned by app.after() for the zoom debounce timer
# we keep it so we can cancel the previous timer if the user click zoom again
_zoom_after_id = None
# the scroll position we saw last time poll_scroll ran
# we compare against this to avoid calling check_visible_page every 100ms
# when the user isn't scrolling
_last_scroll_pos = None

# the vertical gap in pixels between pages on the canvas
PAGE_GAP = 10
# render this many pixels above/below the visible area
BUFFER_PX = 600  
# unload pages this far outside the visible area
UNLOAD_PX = 1200 

# canvas widget stored here so the whole module can reach it
_canvas = None

# stores the position and size of every page on the canvas
# key   = page number (0-indexed)
# value = (x, y, w, h) — top-left corner and size in canvas pixels
# built once in _rebuild() and updated in _on_canvas_resize(
_page_rects = {}

# canvas image item ids  (page_num → canvas item id of the rendered image)
_image_items = {}

# PhotoImage refs — must be kept alive or tkinter GCs them
_photo_refs  = {}

# the queue that check_visible_pages pushes work onto and _worker pulls from
# using a queue means the worker processes pages one at a time in order,
# instead of spawning a new thread per page which causes memory spikes
_render_queue = queue.Queue()

# tracks which page numbers are currently sitting inside _render_queue
# so _enqueue() never adds the same page twice while it's still waiting
_queued_pages = set()

# a lock that protects _queued_pages from being read/written simultaneously
# by the main thread (_enqueue) and the worker thread (_worker)
_queued_lock  = threading.Lock()

def _worker():
    # this loop lives forever inside the app
    while True:
        # block here until check_visible_pages put a page onto the queue
        page_num, gen = _render_queue.get()
        try:
            # remove from the queued set so it can be re-queued later if needed
            with _queued_lock:
                _queued_pages.discard(page_num)
            # if render_generation change or there's nothing in the doc skip it 
            if gen != render_generation or Data.doc is None:
                continue

            # render the page
            page = Data.doc[page_num]
            pix  = page.get_pixmap(matrix=fitz.Matrix(zoom_level, zoom_level))
            # convert to PIL
            img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            del pix
            # check if it is still in the same generation, if so app.after(0, fn) queues fn to run as soon as the main thread is free, which is the safe way to update the UI from a thread
            if gen == render_generation:
                Data.app.after(0, lambda i=img, n=page_num, g=gen: _show_page(i, n, g))
            else:
                del img
        except Exception as e:
            print(f"Render error page {page_num}: {e}")
        finally:
            # always call task_done so queue.join() work correctly if ever used
            _render_queue.task_done()

# start the worker thread
threading.Thread(target=_worker, daemon=True).start()

def _enqueue(page_num, gen):
    # add a page to the render queue
    with _queued_lock:
        # if the page is already in the queue return
        if page_num in _queued_pages:
            return
        # mark is as queue before releasing the lock
        _queued_pages.add(page_num)

    _render_queue.put((page_num, gen))

# empty the render queue
def _drain():
    # clear the tracking set so _enqueue accept new pages immediately
    with _queued_lock:
        _queued_pages.clear()
    # pull everything out of the queue without processing it
    while not _render_queue.empty():
        try:
            _render_queue.get_nowait()
            _render_queue.task_done()
        except queue.Empty:
            break
# function to handle pdf when user click add pdf button
def handle_add_pdf():
    # return the file path and name as filepath and filename
    filepath, filename = add_pdf()
    if not filepath:
        return
    Data.pdf_files[filename] = filepath
    label = ctk.CTkLabel(Data.file_list, text=filename)
    label.pack(anchor="w", padx=5, pady=2)
    # store the filename as key and the label as value inside file_label
    Data.file_labels[filename] = label
    # listen to the left mouse click on the button
    label.bind("<Button-1>", lambda e, name=filename: select_file(name))

# when user clicks a file it saves which file is selected print it
def select_file(filename):
    Data.selected_file = filename
    for lbl in Data.file_labels.values():
        lbl.configure(fg_color="transparent")
        # highlights the file text in gray background
    Data.file_labels[filename].configure(fg_color="gray")
    print(f"selected: {filename}")

# when user click zoom in it increase the zoom level by 20%
def zoom_in():
    global zoom_level, _zoom_after_id
    zoom_level += 0.2
    # debounced so rapid clicks only trigger one render
    if _zoom_after_id:
        Data.app.after_cancel(_zoom_after_id)
    _zoom_after_id = Data.app.after(300, _rebuild)

# when user click zoom out it decrease the zoom level by 20% but it doesn't go beyond 40%
def zoom_out():
    global zoom_level, _zoom_after_id
    zoom_level = max(0.4, zoom_level - 0.2)
    if _zoom_after_id:
        Data.app.after_cancel(_zoom_after_id)
    _zoom_after_id = Data.app.after(300, _rebuild)

# when user clicks open it check if there is a file selected
def open_pdf():
    if not Data.selected_file:
        print("No file selected")
        return
    # close the previous document if there is one
    if Data.doc:
        Data.doc.close()
    Data.doc = fitz.open(Data.pdf_files[Data.selected_file])
    # draw the page placeholders and start lazy rendering 
    _rebuild()

# when user clicks remove it checks if there is a file selected
def remove_pdf():
    if not Data.selected_file:
        print("No file selected")
        return
    # if so remove the file from the pdf_file
    del Data.pdf_files[Data.selected_file]
    # destroy the label widget in the left frame
    Data.file_labels[Data.selected_file].destroy()
    # then delete it fromn the file_labels
    del Data.file_labels[Data.selected_file]
    # then clear the selected file
    Data.selected_file = None

    if Data.doc:
        Data.doc.close()
        Data.doc = None
    # wipe everything off the canvas
    _clear_canvas()

# (only called once by the UI.py once it created the canvas widget) it is use to store canvas reference and bind the resize event
def set_canvas(canvas):
    global _canvas
    _canvas = canvas
    # when the user resize the window, recenter all the page rectangle
    _canvas.bind("<Configure>", lambda e: _on_canvas_resize(e))

# when the window resizes, reposition all page rects to stay centred
def _on_canvas_resize(e):
    # if there is no page to loaded yet, return
    if not _page_rects:
        return
    # the new canvas width in pixels
    canvas_w = e.width

    for page_num, (x, y, w, h) in list(_page_rects.items()):
        # calculate the new x so the page is centered in the canvas
        new_x = max(0, (canvas_w - w) // 2)
        # update the stored rect with the new x position
        _page_rects[page_num] = (new_x, y, w, h)
        # move the gray background rectangle on canvas to a new position
        tag = f"bg_{page_num}"
        _canvas.coords(tag, new_x, y, new_x + w, y + h)
        # if this page has a rendered image on the canvas, move it too
        if page_num in _image_items:
            _canvas.coords(_image_items[page_num], new_x + w // 2, y + h // 2)
    # re-checked which page are visible after the resize
    check_visible_pages()

# delete everything from the canvas and reset all tracking dicts
def _clear_canvas():
    global _page_rects, _image_items, _photo_refs
    if _canvas:
        _canvas.delete("all")
    _page_rects.clear()
    _image_items.clear()
    _photo_refs.clear()

# redraws all page placeholder retangles on the canvas (called when opening a new pdf or zooming)
def _rebuild():
    global render_generation
    render_generation += 1
    _drain()
    _clear_canvas()
    # check if there's no document is open or canvas doesn't exist yet
    if Data.doc is None or _canvas is None:
        return
    # total number of page
    n_pages  = len(Data.doc)
    # current canvas width, fall back 800
    canvas_w = _canvas.winfo_width() or 800

    # y track the vertical position of the next page as we stack them
    y = PAGE_GAP

    for page_num in range(n_pages):
        r = Data.doc[page_num].rect
        # scale the dimension by the current zoom level
        w = int(r.width  * zoom_level)
        h = int(r.height * zoom_level)

        # center the page horizontally on the canvas
        x = max(0, (canvas_w - w) // 2)

        # save the position so check_visible_page can find this page later 
        _page_rects[page_num] = (x, y, w, h)

        # draw a gray rectangle as the placeholder
        _canvas.create_rectangle(
            x, y, x + w, y + h,
            fill="#333333", 
            outline="#555555",
            tags=(f"bg_{page_num}",)
        )

        # page number label in the centre of the placeholder
        _canvas.create_text(
            x + w // 2, y + h // 2,
            text=str(page_num + 1),
            fill="#888888",
            font=("Arial", 14),
            tags=(f"lbl_{page_num}",)
        )

        y += h + PAGE_GAP

    # set the canvas scroll region to the full document height
    _canvas.configure(scrollregion=(0, 0, canvas_w, y))
    check_visible_pages()

# run every 100ms on the main thread
def poll_scroll():
    global _last_scroll_pos
    # if there is a document open and page rects to check
    if Data.doc is not None and _page_rects:
        # return the current scroll position as a tuple (top_fraction, bottom_fraction)
        pos = _canvas.yview()
        # if the scroll position changed since last time, check which page are visible and need rendering
        if pos != _last_scroll_pos:
            _last_scroll_pos = pos
            check_visible_pages()
    # schedule the next poll in 100ms
    Data.app.after(100, poll_scroll)

# look at every page rect and decide whether to render or unload it based on its position relative to the visible area of the canvas
def check_visible_pages():
    if Data.doc is None or not _page_rects or _canvas is None:
        return

    # visible range in canvas content pixels
    sr = _canvas.cget("scrollregion")
    try:
        # if scrollregion is set it looks like "0 0 800 2400", we want the total height which is the 4th number
        if sr:
            total_h = float(sr.split()[3])
        else:
            # else we can get the canvas height in pixels
            total_h = _canvas.winfo_height()
    except Exception:
        total_h = _canvas.winfo_height()
    # if we can't get a valid total height, just return
    if total_h <= 0:
        return
    # yview() return the fractions: (0.0, 0.1) means the top 10% of the canvas content is visible, we multiply by total_h to get the pixel position of the visible area
    t, b = _canvas.yview()
    vis_top = t * total_h
    vis_bot = b * total_h

    # loop through every page rect and check if it's within the buffer zone around the visible area, 
    # if so enqueue it for rendering if it's not already, if it's far outside the visible area and currently rendered, unload it to save memory
    for page_num, (x, y, w, h) in _page_rects.items():
        page_top = y
        page_bot = y + h

        in_view  = page_bot + BUFFER_PX  >= vis_top and page_top - BUFFER_PX  <= vis_bot
        far_away = page_bot + UNLOAD_PX  <  vis_top or  page_top - UNLOAD_PX  >  vis_bot

        if in_view and page_num not in _image_items:
            _enqueue(page_num, render_generation)
        elif far_away and page_num in _image_items:
            _unload_page(page_num)

# when a page is far outside the visible area we call this to remove its image from the canvas and delete the reference so it can be garbage collected and free memory
def _unload_page(page_num):
    if page_num in _image_items:
        _canvas.delete(_image_items[page_num])
        del _image_items[page_num]
    if page_num in _photo_refs:
        del _photo_refs[page_num]

# when the worker thread finish rendering a page it call this to display the image on the canvas, 
# but only if the generation is still the same (the user might have zoomed or opened another file since then)
def _show_page(img, page_num, gen):
    if gen != render_generation or _canvas is None:
        del img
        return
    if page_num not in _page_rects:
        del img
        return

    x, y, w, h = _page_rects[page_num]

    # use tkinter PhotoImage directly — no CTkImage wrapper needed for canvas
    photo = ImageTk.PhotoImage(img)
    del img

    # keep ref so GC doesn't collect it
    _photo_refs[page_num] = photo

    # hide the page number label
    _canvas.delete(f"lbl_{page_num}")

    # draw image centred in the placeholder rect
    item_id = _canvas.create_image(x + w // 2, y + h // 2, image=photo, anchor="center")
    _image_items[page_num] = item_id