from tkinter import filedialog as fida
import os

# open file dialog and ask the user to select a pdf file
def add_pdf():
    filename = fida.askopenfilename(
        initialdir="/", 
        filetypes=[("PDF file", "*.pdf")]
    )
    # if a file is selected, return the file path and name, otherwise return None
    if filename:
        return filename, os.path.basename(filename)
    
    return None, None
    