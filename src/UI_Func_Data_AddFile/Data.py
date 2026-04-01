# store all the shared state here so both ui.py and logic.py can access it without circular imports

# dictionary to store the pdf file name as key and the file path as value
pdf_files = {}

# dictionary to store the filename as key and the label widget as value
file_labels = {}

# store the currently selected file name
selected_files = None

# store the open fitz document
doc = None

# store the CTkImage objects so they don't get garbage collected
pdf_images = []

# store the widget references so logic.py can use them without importing ui.py
pdf_container = None
file_list = None
app = None

# store one placeholder frame per page (page number → CTkFrame)
page_frames = {}

# track which pages have already been rendered (page number → True/False)
page_rendered = {}