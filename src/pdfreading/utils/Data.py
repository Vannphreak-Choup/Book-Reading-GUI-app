'''This is a shared state file that is imported by both UI.py and functionality.py'''

# stores every PDF the user has added when they press the "Add PDF" button
# key = the filename shown in the left panel  (e.g. "mybook.pdf")
# value = the full file path on disk (e.g. "C:/Users/.../mybook.pdf")
pdf_files = {}

# stores the CTkLabel widget for each file shown in the left frame
# key = filename  (same key as pdf_files so we can look up both together)
# value = the CTkLabel widget — we keep this so we can highlight it when the user clicks it, and destroy it when the user removes the file
file_labels = {} 

# currently selected filename
selected_file = None 

# the fitz Document object for the PDF that is currently open and being viewed
# fitz.open() returns this so it gives us access to page count, page sizes, and lets us render individual pages to pixel data
doc = None # open fitz.Document

# widget refs set by UI.py
app = None
# the CTkCanvas on the right side where we render PDF pages
pdf_container = None
# the CTkLabel on the left side that shows the filename
file_list = None
# the CTkEntry in the top-right where the user can type a page number to jump to
page_entry = None
# the CTkLabel in the top-right that shows "Page X / Y"
page_total_label = None
# store the user last read page when they close the app so it stay there
last_read_pages = {}