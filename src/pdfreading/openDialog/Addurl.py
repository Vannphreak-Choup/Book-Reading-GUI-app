import urllib.request
import os
import sys
from importlib.resources import files
from PIL import Image, ImageTk
import threading
import customtkinter as ctk
from ..utils import functionality

# clean the URL nicely remove the query parameters and get the filename, if the filename doesn't end with .pdf we just name it download.pdf, 
# and we also remove any characters that are not alphanumeric or ._- to avoid issues with the filesystem
def _sanitize_filename(url: str) -> str:
    name = url.rstrip("/").split("/")[-1].split("?")[0]
    if not name.lower().endswith(".pdf"):
        name = "download.pdf"

    new_name = ""
    for c in name:
        if c.isalnum() or c in "._- ":
            new_name += c
    name = new_name
    return name or "download.pdf"

# Opens a modal dialog asking the user for a PDF URL.
def open_url_dialog(app, on_success):
    dialog = ctk.CTkToplevel(app)
    dialog.title("Load PDF from URL")
    dialog.geometry("480x220")
    # center the dialog over the main app window
    dialog.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (480 // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (220 // 2)
    dialog.geometry(f"480x220+{x}+{y}")

    dialog.resizable(False, False)
    dialog.transient(app)
    # make the dialog modal by grabbing all events and focusing it
    def _after_init():
        try:
            dialog.grab_set()
        except Exception as e:
            print(f"could not grab: {e}")
        dialog.focus_force()
        dialog.lift()
    
    # set the dialog icon after a short delay to ensure the window has been created
    def _set_dialog_icon():
        try:
            if sys.platform == "win32":
                icon_path = files("pdfreading.assets.title_icon").joinpath("book2.ico")
                dialog.iconbitmap(str(icon_path))
            else:
                icon_path = files("pdfreading.assets.title_icon").joinpath("book2.png")
                dialog.iconphoto(False, ImageTk.PhotoImage(Image.open(icon_path)))
        except Exception as e:
            print(f"Could not set dialog icon: {e}")

    my_font    = ctk.CTkFont(family="Arial", size=13, weight="bold")
    small_font = ctk.CTkFont(family="Arial", size=11)
    # the title and entry box for the URL
    ctk.CTkLabel(dialog, text="PDF URL:", font=my_font).pack(
        anchor="w", padx=20, pady=(20, 2)
    )
    url_entry = ctk.CTkEntry(
        dialog, 
        width=440, 
        font=small_font,
        placeholder_text="https://example.com/file.pdf"
    )
    url_entry.pack(padx=20)
    
    status_label = ctk.CTkLabel(dialog, text="", font=small_font, text_color="gray70")
    status_label.pack(pady=(8, 0))
    # the progress bar
    progress = ctk.CTkProgressBar(dialog, width=440, mode="indeterminate")

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=12)

    # helper function to update the status label and color
    def _set_status(msg, color="gray70"):
        status_label.configure(text=msg, text_color=color)

    # helper function to re-enable the UI elements after a download attempt (whether successful or not)
    def _re_enable():
        progress.stop()
        progress.pack_forget()
        btn_download.configure(state="normal")
        btn_cancel.configure(state="normal")
        url_entry.configure(state="normal")

    """Background thread: download → validate → callback."""
    def _do_download():
        url = url_entry.get().strip()
        # if the URL field is empty, show an error and re-enable the UI so they can try again
        if not url:
            dialog.after(0, lambda: _set_status("Please enter a URL.", "red"))
            dialog.after(0, _re_enable)
            return
        # if the URL doesn't start with http:// or https://, show an error and re-enable the UI so they can try again
        if not url.startswith(("http://", "https://")):
            dialog.after(0, lambda: _set_status("URL must start with http:// or https://", "red"))
            dialog.after(0, _re_enable)
            return

        filename = _sanitize_filename(url)
        filepath = os.path.join(functionality.LIBARY_DIR, filename)
        # try requesting the file
        try:
            # user-agent is set to mimic a real browser to avoid some servers blocking the request
            # the referer header is set to google.com to avoid some servers blocking the request due to missing referer or blocking requests from certain domains
            # the accept header is set to application/pdf to indicate that we only want PDF files, some servers might use this to determine whether to allow the download or not
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                    "referer": "https://www.google.com/",
                    "Accept": "application/pdf,*/*",
                }
            )
            # open the URL
            with urllib.request.urlopen(req) as response:
                with open(filepath, "wb") as f:
                    f.write(response.read())
        except Exception as e:
            err_msg = str(e)
            if "403" in err_msg:
                msg = "Access denied (403). The server block direct downloads. \nTry downloading the file manually and use 'Add PDF' instead."
            elif "404" in err_msg:
                msg = "File not found (404). \nPlease check the URL and try again."
            elif "timeout" in err_msg.lower():
                msg = "Connection timed out. \nPlease check your internet connection and try again."
            else:
                msg = f"Download failed: {err_msg}"

            dialog.after(0, lambda m=msg: _set_status(m, "red"))
            dialog.after(0, _re_enable)
            return

        # open the downloaded file and check if it has a valid PDF header, if not it's not a valid PDF so we delete the file
        try:
            # open the pdf file as binary mode and read the first 5 bytes to check for the PDF header "%PDF-"
            with open(filepath, "rb") as f:
                header = f.read(5)
            if header != b"%PDF-":
                os.remove(filepath)
                dialog.after(0, lambda: _set_status("That URL did not return a PDF file.", "red"))
                dialog.after(0, _re_enable)
                return
        except Exception as e:
            dialog.after(0, lambda err=e: _set_status(f"Error reading file: {err}", "red"))
            dialog.after(0, _re_enable)
            return

        # schedule _finish to run on the main thread as soon as it is free
        dialog.after(0, lambda fp=filepath, fn=filename: _finish(fp, fn))

    # helper function to clean up the dialog and call the on_success callback with the downloaded file path and name
    def _finish(filepath, filename):
        # stop the progress bar
        progress.stop()
        # hide it
        progress.pack_forget()
        # grab_release and destroy the dialog before calling on_success to avoid any potential issues if on_success takes a long time to execute or opens another dialog
        dialog.grab_release()
        dialog.destroy()
        on_success(filepath, filename)   

    # helper function to start the download thread and update the UI accordingly
    def _start():
        url = url_entry.get().strip()
        if not url:
            _set_status("Please enter a URL.", "red")
            return
        btn_download.configure(state="disabled")
        btn_cancel.configure(state="disabled")
        url_entry.configure(state="disabled")
        progress.pack(padx=20, pady=(0, 4))
        progress.start()
        _set_status("Downloading…", "gray70")
        threading.Thread(target=_do_download, daemon=True).start()

    btn_download = ctk.CTkButton(
        btn_frame, 
        text="Download",
        font=my_font, 
        command=_start
    )
    btn_download.pack(side="left", padx=8)

    btn_cancel = ctk.CTkButton(
        btn_frame, 
        text="Cancel", 
        font=my_font,
        fg_color="gray40", 
        hover_color="gray30",
        command=dialog.destroy
    )
    btn_cancel.pack(side="left", padx=8)
    dialog.after(210, _after_init)
    dialog.after(210, _set_dialog_icon)
    dialog.bind("<Return>", lambda e: _start())