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

class URLDialog:
    def __init__(self, app, on_success):
        self.app = app
        self.on_success = on_success
        self._build()
    # Opens a modal dialog asking the user for a PDF URL.
    def _build(self):
        self.dialog = ctk.CTkToplevel(self.app)
        self.dialog.title("Load PDF from URL")
        self.dialog.geometry("480x220")

        # center the dialog over the main app window
        self.dialog.update_idletasks()
        x = self.app.winfo_x() + (self.app.winfo_width() // 2) - (480 // 2)
        y = self.app.winfo_y() + (self.app.winfo_height() // 2) - (220 // 2)
        self.dialog.geometry(f"480x220+{x}+{y}")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.app)

        my_font    = ctk.CTkFont(family="Arial", size=13, weight="bold")
        small_font = ctk.CTkFont(family="Arial", size=11)
        # the title and entry box for the URL
        ctk.CTkLabel(self.dialog, text="PDF URL:", font=my_font).pack(
        anchor="w", padx=20, pady=(20, 2)
        )
        url_entry = ctk.CTkEntry(
        self.dialog, 
        width=440, 
        font=small_font,
        placeholder_text="https://example.com/file.pdf"
        )
        url_entry.pack(padx=20)
    
        status_label = ctk.CTkLabel(self.dialog, text="", font=small_font, text_color="gray70")
        status_label.pack(pady=(8, 0))
        # the progress bar
        self.progress = ctk.CTkProgressBar(self.dialog, width=440, mode="indeterminate")

        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=12)

        btn_download = ctk.CTkButton(
        btn_frame, 
        text="Download",
        font=my_font, 
        command=self._start
    )
        btn_download.pack(side="left", padx=8)

        btn_cancel = ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            font=my_font,
            fg_color="gray40", 
            hover_color="gray30",
            command=self.dialog.destroy
        )
        btn_cancel.pack(side="left", padx=8)
        self.dialog.after(210, self._after_init)
        self.dialog.after(210, self._set_dialog_icon)
        self.dialog.bind("<Return>", lambda e: self._start())

    # make the dialog modal by grabbing all events and focusing it
    def _after_init(self):
        try:
            self.dialog.grab_set()
        except Exception as e:
            print(f"could not grab: {e}")
        self.dialog.focus_force()
        self.dialog.lift()
    
    # set the dialog icon after a short delay to ensure the window has been created
    def _set_dialog_icon(self):
        try:
            if sys.platform == "win32":
                icon_path = files("pdfreading.assets.title_icon").joinpath("book2.ico")
                self.dialog.iconbitmap(str(icon_path))
            else:
                icon_path = files("pdfreading.assets.title_icon").joinpath("book2.png")
                self.dialog.iconphoto(False, ImageTk.PhotoImage(Image.open(icon_path)))
        except Exception as e:
            print(f"Could not set dialog icon: {e}")

    # helper function to update the status label and color
    def _set_status(self, msg, color="gray70"):
        self.status_label.configure(text=msg, text_color=color)

    # helper function to re-enable the UI elements after a download attempt (whether successful or not)
    def _re_enable(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_download.configure(state="normal")
        self.btn_cancel.configure(state="normal")
        self.url_entry.configure(state="normal")

    """Background thread: download → validate → callback."""
    def _do_download(self):
        url = self.url_entry.get().strip()
        # if the URL field is empty, show an error and re-enable the UI so they can try again
        if not url:
            self.dialog.after(0, lambda: self._set_status("Please enter a URL.", "red"))
            self.dialog.after(0, self._re_enable)
            return
        # if the URL doesn't start with http:// or https://, show an error and re-enable the UI so they can try again
        if not url.startswith(("http://", "https://")):
            self.dialog.after(0, lambda: self._set_status("URL must start with http:// or https://", "red"))
            self.dialog.after(0, self._re_enable)
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

            self.dialog.after(0, lambda m=msg: self._set_status(m, "red"))
            self.dialog.after(0, self._re_enable)
            return

        # open the downloaded file and check if it has a valid PDF header, if not it's not a valid PDF so we delete the file
        try:
            # open the pdf file as binary mode and read the first 5 bytes to check for the PDF header "%PDF-"
            with open(filepath, "rb") as f:
                header = f.read(5)
            if header != b"%PDF-":
                os.remove(filepath)
                self.dialog.after(0, lambda: self._set_status("That URL did not return a PDF file.", "red"))
                self.dialog.after(0, self._re_enable)
                return
        except Exception as e:
            self.dialog.after(0, lambda err=e: self._set_status(f"Error reading file: {err}", "red"))
            self.dialog.after(0, self._re_enable)
            return

        # schedule _finish to run on the main thread as soon as it is free
        self.dialog.after(0, lambda fp=filepath, fn=filename: self._finish(fp, fn))

    # helper function to clean up the dialog and call the on_success callback with the downloaded file path and name
    def _finish(self, filepath, filename):
        # stop the progress bar
        self.progress.stop()
        # hide it
        self.progress.pack_forget()
        # grab_release and destroy the dialog before calling on_success to avoid any potential issues if on_success takes a long time to execute or opens another dialog
        self.dialog.grab_release()
        self.dialog.destroy()
        self.on_success(filepath, filename)

    # helper function to start the download thread and update the UI accordingly
    def _start(self):
        url = self.url_entry.get().strip()
        if not url:
            self._set_status("Please enter a URL.", "red")
            return
        self.btn_download.configure(state="disabled")
        self.btn_cancel.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.progress.pack(padx=20, pady=(0, 4))
        self.progress.start()
        self._set_status("Downloading…", "gray70")
        threading.Thread(target=self._do_download, daemon=True).start()

# this is where functionality called to use the URL dialog
def open_url_dialog(app, on_success):
    URLDialog(app, on_success)